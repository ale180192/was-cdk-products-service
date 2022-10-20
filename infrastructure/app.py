#!/usr/bin/env python3

import aws_cdk as cdk
from aws_cdk import (
    Environment,
    pipelines,
    Stage
)
from constructs import Construct

from conf.aws_normalize import build_naming_convention
from stages.product_stack_stage import ProductStackStage


app = cdk.App()
props = {}

SANDBOX_NAMESPACE = "sandbox"
PIPELINE_NAMESPACE = "pipeline"
PRODUCTION_NAMESPACE = "prod"

PROJECT_NAME = "products"

# Accounts
PIPELINE_ACCOUNT = "195480428059"
SANDBOX_ACCOUNT = "057864228752"
PRODUCTION_ACCOUNT = "009939884268"

# Regions
PIPELINE_REGION = "us-east-1"
SANDBOX_REGION = "us-east-1"
PRODUCTION_REGION = "us-east-1"

class PipelineStack(cdk.Stack):
    def __init__(
        self, scope: Construct, id: str, **kwargs
    ) -> None:
        pipeline_name = build_naming_convention(
            project_name=PROJECT_NAME,
            namespace=PIPELINE_NAMESPACE,
            sufix="products-pipeline"
        )
        super().__init__(scope, id, **kwargs)
        connection_arn = "arn:aws:codestar-connections:us-east-1:195480428059:connection/c3b69299-09d0-4e8c-bc82-bf26a1b02ad8"
        connection_source = pipelines.CodePipelineSource.connection(
            repo_string="ale180192/was-cdk-products-service",
            branch="master",
            connection_arn=connection_arn
        )
        pipeline = pipelines.CodePipeline(
            scope=self,
            id=pipeline_name,
            synth=pipelines.CodeBuildStep(
                "Synth",
                input=connection_source,
                install_commands=["npm install -g aws-cdk"],
                commands=["ls", "cd infrastructure", "python -m pip install -r requirements.txt", "cdk synth"],
                primary_output_directory="infrastructure/cdk.out"
            ),
            pipeline_name=pipeline_name,
            cross_account_keys=True,
        )
        # Sandbox stage
        env_sandbox = Environment(
            account=SANDBOX_ACCOUNT, region=SANDBOX_REGION
        )
        sandbox_stage_name = build_naming_convention(
            project_name=PROJECT_NAME,
            namespace=SANDBOX_NAMESPACE,
            sufix="stage-products"
        )
        sandbox_stage = ProductStackStage(
            scope=self,
            id=sandbox_stage_name,
            project_name=PROJECT_NAME,
            namespace=SANDBOX_NAMESPACE,
            env=env_sandbox
        )
        pipeline.add_stage(sandbox_stage)
        
        # Production stage
        env_sandbox = Environment(
            account=PRODUCTION_ACCOUNT, region=PRODUCTION_REGION
        )
        production_stage_name = build_naming_convention(
            project_name=PROJECT_NAME,
            namespace=PRODUCTION_NAMESPACE,
            sufix="stage-products"
        )
        production_stage = ProductStackStage(
            scope=self,
            id=production_stage_name,
            project_name=PROJECT_NAME,
            namespace=PRODUCTION_NAMESPACE,
            env=env_sandbox
        )
        manually_step_name = build_naming_convention(
            project_name=PROJECT_NAME,
            namespace=PIPELINE_NAMESPACE,
            sufix="manual-approve-step"
        )
        pipeline.add_stage(
            production_stage,
            pre=[pipelines.ManualApprovalStep(id=manually_step_name),]
        )


name_pipeline = build_naming_convention(
    project_name=PROJECT_NAME,
    namespace=PIPELINE_NAMESPACE,
    sufix="pipeline-products"
)

env_pipe = Environment(
    account=PIPELINE_ACCOUNT, region=PIPELINE_REGION
)

PipelineStack(
    scope=app,
    id=name_pipeline,
    env=env_pipe
)

app.synth()

