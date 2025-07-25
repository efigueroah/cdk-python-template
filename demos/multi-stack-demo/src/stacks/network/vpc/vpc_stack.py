import os

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    CfnOutput,
)
from constructs import Construct
from cdk_nag import NagSuppressions


class NetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC with public subnet only
        self.vpc = ec2.Vpc(
            self,
            "DemoVPC",
            vpc_name=f"demo-vpc-{self.account}-{self.region}",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=2,  # Use 2 AZs for high availability
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ],
            # Enable DNS support
            enable_dns_hostnames=True,
            enable_dns_support=True,
        )

        # Create Internet Gateway (automatically created with PUBLIC subnet)
        # Add tags to VPC
        self.vpc.node.add_metadata("Description", "Demo VPC for multi-stack example")

        # CDK Nag suppressions for VPC
        NagSuppressions.add_resource_suppressions(
            self.vpc,
            [
                {
                    "id": "AwsSolutions-VPC7",
                    "reason": "VPC Flow Logs not required for demo environment"
                }
            ]
        )

        # Output VPC ID for use in other stacks
        CfnOutput(
            self,
            "VpcId",
            value=self.vpc.vpc_id,
            description="ID of the created VPC",
            export_name=f"{construct_id}-VpcId"
        )

        # Output public subnet IDs
        public_subnet_ids = [subnet.subnet_id for subnet in self.vpc.public_subnets]
        CfnOutput(
            self,
            "PublicSubnetIds",
            value=",".join(public_subnet_ids),
            description="IDs of the public subnets",
            export_name=f"{construct_id}-PublicSubnetIds"
        )

        # Output availability zones
        availability_zones = [subnet.availability_zone for subnet in self.vpc.public_subnets]
        CfnOutput(
            self,
            "AvailabilityZones",
            value=",".join(availability_zones),
            description="Availability zones of the public subnets",
            export_name=f"{construct_id}-AvailabilityZones"
        )

    @property
    def vpc_id(self) -> str:
        """Return VPC ID for cross-stack reference."""
        return self.vpc.vpc_id

    @property
    def public_subnets(self) -> list:
        """Return public subnets for cross-stack reference."""
        return self.vpc.public_subnets
