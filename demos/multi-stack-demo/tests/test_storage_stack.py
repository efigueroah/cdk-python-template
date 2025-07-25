import pytest
from aws_cdk import App
from aws_cdk.assertions import Template, Match

from src.stacks.storage.s3 import StorageStack


@pytest.fixture(scope="module")
def storage_template():
    app = App()
    stack = StorageStack(app, "test-storage-stack")
    template = Template.from_stack(stack)
    yield template


def test_two_buckets_created(storage_template):
    """Test that exactly two S3 buckets are created."""
    storage_template.resource_count_is("AWS::S3::Bucket", 2)


def test_primary_bucket_configuration(storage_template):
    """Test primary bucket has correct configuration."""
    # Test bucket with CloudFormation function for name
    storage_template.has_resource_properties("AWS::S3::Bucket", {
        "BucketName": Match.object_like({
            "Fn::Join": Match.any_value()
        }),
        "BucketEncryption": {
            "ServerSideEncryptionConfiguration": [
                {
                    "ServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }
            ]
        },
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "BlockPublicPolicy": True,
            "IgnorePublicAcls": True,
            "RestrictPublicBuckets": True
        },
        "VersioningConfiguration": {
            "Status": "Enabled"
        }
    })


def test_backup_bucket_configuration(storage_template):
    """Test backup bucket has correct configuration."""
    # Test that we have buckets with proper encryption
    resources = storage_template.to_json()["Resources"]
    bucket_count = 0
    
    for resource_id, resource in resources.items():
        if resource["Type"] == "AWS::S3::Bucket":
            bucket_count += 1
            # Check encryption
            assert "BucketEncryption" in resource["Properties"]
            encryption = resource["Properties"]["BucketEncryption"]
            assert encryption["ServerSideEncryptionConfiguration"][0]["ServerSideEncryptionByDefault"]["SSEAlgorithm"] == "AES256"
            
            # Check public access block
            assert "PublicAccessBlockConfiguration" in resource["Properties"]
            pab = resource["Properties"]["PublicAccessBlockConfiguration"]
            assert pab["BlockPublicAcls"] == True
            assert pab["BlockPublicPolicy"] == True
            assert pab["IgnorePublicAcls"] == True
            assert pab["RestrictPublicBuckets"] == True
            
            # Check versioning
            assert "VersioningConfiguration" in resource["Properties"]
            assert resource["Properties"]["VersioningConfiguration"]["Status"] == "Enabled"
    
    assert bucket_count == 2, "Should have exactly 2 buckets"


def test_primary_bucket_lifecycle(storage_template):
    """Test primary bucket has correct lifecycle configuration."""
    storage_template.has_resource_properties("AWS::S3::Bucket", {
        "LifecycleConfiguration": {
            "Rules": [
                {
                    "Id": "PrimaryDataLifecycle",
                    "Status": "Enabled",
                    "Transitions": [
                        {
                            "StorageClass": "STANDARD_IA",
                            "TransitionInDays": 30
                        },
                        {
                            "StorageClass": "GLACIER",
                            "TransitionInDays": 90
                        }
                    ]
                }
            ]
        }
    })


def test_backup_bucket_lifecycle(storage_template):
    """Test backup bucket has aggressive lifecycle configuration."""
    storage_template.has_resource_properties("AWS::S3::Bucket", {
        "LifecycleConfiguration": {
            "Rules": [
                {
                    "Id": "BackupDataLifecycle",
                    "Status": "Enabled",
                    "Transitions": [
                        {
                            "StorageClass": "STANDARD_IA",
                            "TransitionInDays": 7
                        },
                        {
                            "StorageClass": "GLACIER",
                            "TransitionInDays": 30
                        },
                        {
                            "StorageClass": "DEEP_ARCHIVE",
                            "TransitionInDays": 180
                        }
                    ]
                }
            ]
        }
    })


def test_bucket_policies_ssl_enforcement(storage_template):
    """Test that both buckets have SSL enforcement policies."""
    # Should have 2 bucket policies (one for each bucket)
    storage_template.resource_count_is("AWS::S3::BucketPolicy", 2)
    
    # Both should have SSL enforcement
    storage_template.has_resource_properties("AWS::S3::BucketPolicy", {
        "PolicyDocument": {
            "Statement": Match.array_with([
                Match.object_like({
                    "Action": "s3:*",
                    "Condition": {
                        "Bool": {
                            "aws:SecureTransport": "false"
                        }
                    },
                    "Effect": "Deny",
                    "Principal": {
                        "AWS": "*"
                    }
                })
            ])
        }
    })


def test_stack_outputs(storage_template):
    """Test that stack outputs are defined for both buckets."""
    outputs = storage_template.to_json()["Outputs"]
    
    # Check that required outputs exist
    assert "PrimaryBucketName" in outputs
    assert "PrimaryBucketArn" in outputs
    assert "BackupBucketName" in outputs
    assert "BackupBucketArn" in outputs
    
    # Check output descriptions
    assert "primary storage bucket" in outputs["PrimaryBucketName"]["Description"]
    assert "backup storage bucket" in outputs["BackupBucketName"]["Description"]


def test_cdk_nag_suppressions_present(storage_template):
    """Test that CDK Nag suppressions are present in both buckets."""
    resources = storage_template.to_json()["Resources"]
    
    # Find S3 bucket resources
    bucket_resources = []
    for resource_id, resource in resources.items():
        if resource["Type"] == "AWS::S3::Bucket":
            bucket_resources.append(resource)
    
    assert len(bucket_resources) == 2, "Should have exactly 2 bucket resources"
    
    # Check that both buckets have CDK Nag suppressions
    for bucket_resource in bucket_resources:
        if "Metadata" in bucket_resource and "cdk_nag" in bucket_resource["Metadata"]:
            suppressions = bucket_resource["Metadata"]["cdk_nag"]["rules_to_suppress"]
            suppression_ids = [rule["id"] for rule in suppressions]
            
            # Verify expected suppressions
            assert "AwsSolutions-S1" in suppression_ids
            assert "AwsSolutions-S2" in suppression_ids
            assert "AwsSolutions-S10" in suppression_ids


def test_bucket_naming_conventions(storage_template):
    """Test that buckets have proper naming structure with CloudFormation functions."""
    resources = storage_template.to_json()["Resources"]
    
    bucket_names_with_cf = 0
    for resource_id, resource in resources.items():
        if resource["Type"] == "AWS::S3::Bucket":
            bucket_name = resource["Properties"]["BucketName"]
            # Check if it's a CloudFormation function
            if isinstance(bucket_name, dict) and "Fn::Join" in bucket_name:
                bucket_names_with_cf += 1
    
    assert bucket_names_with_cf == 2, "Both buckets should use CloudFormation functions for naming"


def test_auto_delete_configuration(storage_template):
    """Test that both buckets have auto-delete configuration for dev."""
    resources = storage_template.to_json()["Resources"]
    
    buckets_with_auto_delete = 0
    for resource_id, resource in resources.items():
        if resource["Type"] == "AWS::S3::Bucket":
            tags = resource["Properties"].get("Tags", [])
            for tag in tags:
                if tag["Key"] == "aws-cdk:auto-delete-objects" and tag["Value"] == "true":
                    buckets_with_auto_delete += 1
                    break
    
    assert buckets_with_auto_delete == 2, "Both buckets should have auto-delete configuration"


def test_different_lifecycle_configurations(storage_template):
    """Test that buckets have different lifecycle configurations."""
    resources = storage_template.to_json()["Resources"]
    
    # Find bucket resources and their lifecycle configurations
    lifecycle_configs = []
    for resource_id, resource in resources.items():
        if resource["Type"] == "AWS::S3::Bucket":
            if "LifecycleConfiguration" in resource["Properties"]:
                rules = resource["Properties"]["LifecycleConfiguration"]["Rules"]
                lifecycle_configs.append(rules[0]["Id"])  # Get the rule ID
    
    # Should have two different lifecycle rule IDs
    assert len(lifecycle_configs) == 2
    assert "PrimaryDataLifecycle" in lifecycle_configs
    assert "BackupDataLifecycle" in lifecycle_configs
