import os

from aws_cdk import App, Environment
from cdk_nag import AwsSolutionsChecks

from my_datalake.main import MyStack

# for development, use account/region from cdk cli
dev_env = Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)

app = App()

# Create the stack
stack = MyStack(app, "my-datalake-dev", env=dev_env)

# Apply CDK Nag checks
AwsSolutionsChecks(verbose=True).visit(stack)

# MyStack(app, "my-datalake-prod", env=prod_env)

app.synth()
