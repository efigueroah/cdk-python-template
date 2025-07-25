import os

from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_s3 as s3,
)
from constructs import Construct
from cdk_nag import NagSuppressions


class MyStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket for data lake with security best practices
        data_lake_bucket = s3.Bucket(
            self,
            "DataLakeBucket",
            bucket_name=f"my-datalake-{self.account}-{self.region}",
            # Security configurations
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=True,
            # Lifecycle management
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="TransitionToIA",
                    enabled=True,
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30)
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(90)
                        )
                    ]
                )
            ],
            # For dev environment, allow deletion
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # CDK Nag suppressions for development environment
        NagSuppressions.add_resource_suppressions(
            data_lake_bucket,
            [
                {
                    "id": "AwsSolutions-S1",
                    "reason": "Server access logging is not required for development environment"
                },
                {
                    "id": "AwsSolutions-S2",
                    "reason": "Public read access is blocked by default configuration"
                },
                {
                    "id": "AwsSolutions-S10",
                    "reason": "SSL enforcement is enabled via enforce_ssl=True"
                }
            ]
        )

        # Suppress auto-delete objects for development
        NagSuppressions.add_resource_suppressions_by_path(
            self,
            f"/{construct_id}/DataLakeBucket/Policy/Resource",
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Auto-delete objects policy requires wildcard permissions for development cleanup"
                }
            ]
        )
