#!/usr/bin/env python3
import os

import aws_cdk as cdk
from aws_cdk import (
    pipelines
)
from constructs import Construct

from configuration.aws_normalize import build_naming_convention


app = cdk.App()
props = {}

SANDBOX_NAMESPACE = "sandbox"
PIPELINE_NAMESPACE = "pipeline"
PRODUCTION_NAMESPACE = "prod"

PROJECT_NAME = "products"

from infra.products_stack.products_stack import AwsCdkProductsServiceStack

class PipelineStack(cdk.Stack):
    def __init__(
        self, scope: Construct, construct_id: str, props, **kwargs
    ) -> None:
        pipeline_name = build_naming_convention(
            project_name=PROJECT_NAME, namespace=PIPELINE_NAMESPACE, sufix="products-pipeline"
        )
        super().__init__(scope, construct_id, **kwargs)
        pipeline = pipelines.CodePipeline(
            scope=self,
            id=pipeline_name,
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.connection(
                    repo_string="products-service", branch="master", connection_arn="arn:aws:codestar:us-east-1:195480428059:project/products-servic"
                ),
                commands=[
                    "npm ci && npm ci --prefix lambda",
                    "npx cdk synth"
                ]
            ),
            pipeline_name=pipeline_name,
        )


app.synth()

