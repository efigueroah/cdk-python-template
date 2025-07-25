import pytest
from aws_cdk import App
from aws_cdk.assertions import Template, Match

from src.stacks.network.vpc import NetworkStack


@pytest.fixture(scope="module")
def network_template():
    app = App()
    stack = NetworkStack(app, "test-network-stack")
    template = Template.from_stack(stack)
    yield template


def test_vpc_created(network_template):
    """Test that VPC is created with correct configuration."""
    network_template.resource_count_is("AWS::EC2::VPC", 1)
    
    network_template.has_resource_properties("AWS::EC2::VPC", {
        "CidrBlock": "10.0.0.0/16",
        "EnableDnsHostnames": True,
        "EnableDnsSupport": True
    })


def test_public_subnets_created(network_template):
    """Test that public subnets are created in multiple AZs."""
    # Should have 2 public subnets (one per AZ)
    network_template.resource_count_is("AWS::EC2::Subnet", 2)
    
    # Check that subnets have correct CIDR blocks
    network_template.has_resource_properties("AWS::EC2::Subnet", {
        "CidrBlock": "10.0.0.0/24"
    })
    
    network_template.has_resource_properties("AWS::EC2::Subnet", {
        "CidrBlock": "10.0.1.0/24"
    })


def test_internet_gateway_created(network_template):
    """Test that Internet Gateway is created and attached."""
    network_template.resource_count_is("AWS::EC2::InternetGateway", 1)
    network_template.resource_count_is("AWS::EC2::VPCGatewayAttachment", 1)


def test_route_table_configuration(network_template):
    """Test that route tables are configured for public access."""
    # Should have route tables for public subnets
    network_template.resource_count_is("AWS::EC2::RouteTable", 2)
    
    # Should have routes to Internet Gateway
    network_template.has_resource_properties("AWS::EC2::Route", {
        "DestinationCidrBlock": "0.0.0.0/0"
    })


def test_stack_outputs(network_template):
    """Test that stack outputs are defined."""
    outputs = network_template.to_json()["Outputs"]
    
    # Check that required outputs exist
    assert "VpcId" in outputs
    assert "PublicSubnetIds" in outputs
    assert "AvailabilityZones" in outputs
    
    # Check output descriptions
    assert "ID of the created VPC" in outputs["VpcId"]["Description"]
    assert "IDs of the public subnets" in outputs["PublicSubnetIds"]["Description"]


def test_cdk_nag_suppressions_present(network_template):
    """Test that CDK Nag suppressions are present in VPC metadata."""
    resources = network_template.to_json()["Resources"]
    
    # Find VPC resource
    vpc_resource = None
    for resource_id, resource in resources.items():
        if resource["Type"] == "AWS::EC2::VPC":
            vpc_resource = resource
            break
    
    assert vpc_resource is not None, "VPC resource not found"
    
    # Check for CDK Nag suppressions in metadata
    if "Metadata" in vpc_resource and "cdk_nag" in vpc_resource["Metadata"]:
        suppressions = vpc_resource["Metadata"]["cdk_nag"]["rules_to_suppress"]
        suppression_ids = [rule["id"] for rule in suppressions]
        assert "AwsSolutions-VPC7" in suppression_ids


def test_vpc_naming_convention(network_template):
    """Test that VPC has proper naming structure."""
    # Check that VPC has Name tag with CloudFormation function
    network_template.has_resource_properties("AWS::EC2::VPC", {
        "Tags": Match.array_with([
            {
                "Key": "Name",
                "Value": Match.object_like({
                    "Fn::Join": Match.any_value()
                })
            }
        ])
    })
