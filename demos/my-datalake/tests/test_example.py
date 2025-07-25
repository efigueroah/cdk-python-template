import pytest
from aws_cdk import App
from aws_cdk.assertions import Template, Match

from my_datalake.main import MyStack


@pytest.fixture(scope="module")
def template():
    app = App()
    stack = MyStack(app, "my-stack-test")
    template = Template.from_stack(stack)
    yield template


def test_s3_bucket_created(template):
    """Test that exactly one S3 bucket is created."""
    template.resource_count_is("AWS::S3::Bucket", 1)


def test_s3_bucket_properties(template):
    """Test S3 bucket has correct security properties."""
    template.has_resource_properties("AWS::S3::Bucket", {
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


def test_s3_bucket_lifecycle(template):
    """Test S3 bucket has lifecycle configuration."""
    template.has_resource_properties("AWS::S3::Bucket", {
        "LifecycleConfiguration": {
            "Rules": [
                {
                    "Id": "TransitionToIA",
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


def test_bucket_policy_ssl_enforcement(template):
    """Test that bucket policy enforces SSL."""
    template.has_resource_properties("AWS::S3::BucketPolicy", {
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


def test_cdk_nag_suppressions_present(template):
    """Test that CDK Nag suppressions are present in metadata."""
    # Get all resources and check for CDK Nag metadata
    resources = template.to_json()["Resources"]
    
    # Find bucket resource
    bucket_resource = None
    for resource_id, resource in resources.items():
        if resource["Type"] == "AWS::S3::Bucket":
            bucket_resource = resource
            break
    
    assert bucket_resource is not None, "S3 bucket resource not found"
    assert "Metadata" in bucket_resource, "Metadata not found in bucket resource"
    assert "cdk_nag" in bucket_resource["Metadata"], "CDK Nag metadata not found"
    
    suppressions = bucket_resource["Metadata"]["cdk_nag"]["rules_to_suppress"]
    suppression_ids = [rule["id"] for rule in suppressions]
    
    # Verify expected suppressions
    assert "AwsSolutions-S1" in suppression_ids
    assert "AwsSolutions-S2" in suppression_ids
    assert "AwsSolutions-S10" in suppression_ids
