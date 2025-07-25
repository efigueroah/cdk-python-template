import os

from aws_cdk import App, Environment
from cdk_nag import AwsSolutionsChecks

from src.stacks.network.vpc import NetworkStack
from src.stacks.storage.s3 import StorageStack

# for development, use account/region from cdk cli
dev_env = Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)

app = App()

# Create the network stack first
network_stack = NetworkStack(app, "multi-stack-demo-network", env=dev_env)

# Create the storage stack (can be independent or reference network stack)
storage_stack = StorageStack(app, "multi-stack-demo-storage", env=dev_env)

# Apply CDK Nag checks to both stacks
AwsSolutionsChecks(verbose=True).visit(network_stack)
AwsSolutionsChecks(verbose=True).visit(storage_stack)

app.synth()
