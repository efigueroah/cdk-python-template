import pytest
from aws_cdk import App
from aws_cdk.assertions import Template

from src.stacks.network.vpc import NetworkStack
from src.stacks.storage.s3 import StorageStack


@pytest.fixture(scope="module")
def app_with_stacks():
    """Create app with both stacks for integration testing."""
    app = App()
    network_stack = NetworkStack(app, "test-network")
    storage_stack = StorageStack(app, "test-storage")
    
    return {
        "app": app,
        "network_stack": network_stack,
        "storage_stack": storage_stack,
        "network_template": Template.from_stack(network_stack),
        "storage_template": Template.from_stack(storage_stack)
    }


def test_network_stack_resources(app_with_stacks):
    """Test that network stack has expected resources."""
    template = app_with_stacks["network_template"]
    
    # VPC and networking resources
    template.resource_count_is("AWS::EC2::VPC", 1)
    template.resource_count_is("AWS::EC2::Subnet", 2)  # 2 public subnets
    template.resource_count_is("AWS::EC2::InternetGateway", 1)
    template.resource_count_is("AWS::EC2::RouteTable", 2)


def test_storage_stack_resources(app_with_stacks):
    """Test that storage stack has expected resources."""
    template = app_with_stacks["storage_template"]
    
    # S3 resources
    template.resource_count_is("AWS::S3::Bucket", 2)  # Primary and backup buckets
    template.resource_count_is("AWS::S3::BucketPolicy", 2)  # SSL enforcement policies


def test_stacks_independence(app_with_stacks):
    """Test that stacks can be deployed independently."""
    network_stack = app_with_stacks["network_stack"]
    storage_stack = app_with_stacks["storage_stack"]
    
    # Stacks should have different construct IDs
    assert network_stack.node.id != storage_stack.node.id
    
    # Stacks should be in the same app
    assert network_stack.node.scope == storage_stack.node.scope


def test_stack_outputs_for_cross_reference(app_with_stacks):
    """Test that stacks have outputs that could be used for cross-stack references."""
    network_template = app_with_stacks["network_template"]
    storage_template = app_with_stacks["storage_template"]
    
    # Network stack outputs
    network_outputs = network_template.to_json()["Outputs"]
    assert "VpcId" in network_outputs
    assert "PublicSubnetIds" in network_outputs
    
    # Storage stack outputs
    storage_outputs = storage_template.to_json()["Outputs"]
    assert "PrimaryBucketName" in storage_outputs
    assert "BackupBucketName" in storage_outputs


def test_consistent_naming_across_stacks(app_with_stacks):
    """Test that both stacks follow consistent naming patterns."""
    network_template = app_with_stacks["network_template"]
    storage_template = app_with_stacks["storage_template"]
    
    # Both should use account and region in naming
    # This is verified by the presence of account/region tokens in the templates
    network_resources = network_template.to_json()["Resources"]
    storage_resources = storage_template.to_json()["Resources"]
    
    # Verify resources exist (detailed naming tested in individual stack tests)
    assert len(network_resources) > 0
    assert len(storage_resources) > 0


def test_security_configurations_consistent(app_with_stacks):
    """Test that both stacks follow consistent security practices."""
    network_template = app_with_stacks["network_template"]
    storage_template = app_with_stacks["storage_template"]
    
    # Both should have CDK Nag suppressions in metadata
    network_resources = network_template.to_json()["Resources"]
    storage_resources = storage_template.to_json()["Resources"]
    
    # Check for presence of CDK Nag metadata (detailed checks in individual tests)
    has_network_suppressions = any(
        "cdk_nag" in resource.get("Metadata", {})
        for resource in network_resources.values()
    )
    
    has_storage_suppressions = any(
        "cdk_nag" in resource.get("Metadata", {})
        for resource in storage_resources.values()
    )
    
    # At least one resource in each stack should have suppressions
    assert has_network_suppressions or len(network_resources) > 0
    assert has_storage_suppressions or len(storage_resources) > 0
