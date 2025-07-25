import os

from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_s3 as s3,
    CfnOutput,
)
from constructs import Construct
from cdk_nag import NagSuppressions


class StorageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Primary storage bucket for application data
        self.primary_bucket = s3.Bucket(
            self,
            "PrimaryBucket",
            bucket_name=f"primary-storage-{self.account}-{self.region}",
            # Security configurations
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=True,
            # Lifecycle management for primary data
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="PrimaryDataLifecycle",
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

        # Secondary bucket for backups and logs
        self.backup_bucket = s3.Bucket(
            self,
            "BackupBucket",
            bucket_name=f"backup-storage-{self.account}-{self.region}",
            # Security configurations
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=True,
            # Aggressive lifecycle for backup data
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="BackupDataLifecycle",
                    enabled=True,
                    transitions=[
                        # Move to IA quickly for backups
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(7)
                        ),
                        # Move to Glacier for long-term retention
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(30)
                        ),
                        # Deep archive for very old backups
                        s3.Transition(
                            storage_class=s3.StorageClass.DEEP_ARCHIVE,
                            transition_after=Duration.days(180)
                        )
                    ]
                )
            ],
            # For dev environment, allow deletion
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # CDK Nag suppressions for primary bucket
        NagSuppressions.add_resource_suppressions(
            self.primary_bucket,
            [
                {
                    "id": "AwsSolutions-S1",
                    "reason": "Server access logging not required for demo environment"
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

        # CDK Nag suppressions for backup bucket
        NagSuppressions.add_resource_suppressions(
            self.backup_bucket,
            [
                {
                    "id": "AwsSolutions-S1",
                    "reason": "Server access logging not required for demo environment"
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

        # Suppress auto-delete objects for both buckets
        for bucket_name in ["PrimaryBucket", "BackupBucket"]:
            NagSuppressions.add_resource_suppressions_by_path(
                self,
                f"/{construct_id}/{bucket_name}/Policy/Resource",
                [
                    {
                        "id": "AwsSolutions-IAM5",
                        "reason": "Auto-delete objects policy requires wildcard permissions for development cleanup"
                    }
                ]
            )

        # Outputs for primary bucket
        CfnOutput(
            self,
            "PrimaryBucketName",
            value=self.primary_bucket.bucket_name,
            description="Name of the primary storage bucket",
            export_name=f"{construct_id}-PrimaryBucketName"
        )

        CfnOutput(
            self,
            "PrimaryBucketArn",
            value=self.primary_bucket.bucket_arn,
            description="ARN of the primary storage bucket",
            export_name=f"{construct_id}-PrimaryBucketArn"
        )

        # Outputs for backup bucket
        CfnOutput(
            self,
            "BackupBucketName",
            value=self.backup_bucket.bucket_name,
            description="Name of the backup storage bucket",
            export_name=f"{construct_id}-BackupBucketName"
        )

        CfnOutput(
            self,
            "BackupBucketArn",
            value=self.backup_bucket.bucket_arn,
            description="ARN of the backup storage bucket",
            export_name=f"{construct_id}-BackupBucketArn"
        )

    @property
    def primary_bucket_name(self) -> str:
        """Return primary bucket name for cross-stack reference."""
        return self.primary_bucket.bucket_name

    @property
    def backup_bucket_name(self) -> str:
        """Return backup bucket name for cross-stack reference."""
        return self.backup_bucket.bucket_name
