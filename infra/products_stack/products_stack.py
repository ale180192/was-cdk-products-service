import os

from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_apigateway as gateway,
)
import aws_cdk
from constructs import Construct

from conf.aws_normalize import build_naming_convention


dirname = os.path.dirname(__file__)

class ProductsStack(Stack):

    def __init__(
        self, scope: Construct, construct_id: str, props, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        api_gateway_convention = build_naming_convention(sufix="gw-products")
        api = gateway.RestApi(
            scope=self,
            id=api_gateway_convention,
            rest_api_name=api_gateway_convention,
            api_key_source_type=gateway.ApiKeySourceType.HEADER,
            default_cors_preflight_options={
                "allow_origins": gateway.Cors.ALL_ORIGINS,
                "allow_methods": gateway.Cors.ALL_METHODS
            }
        )

        method_responses = [{"statusCode": "200"}]

        api_v1_route = api.root.add_resource("api").add_resource("v1")
        api_v1_products_route = api_v1_route.add_resource("products")
        lambda_role_convention_name = build_naming_convention(sufix="lambda-role")
        lambda_role = iam.Role(
            scope=self,
            id=lambda_role_convention_name,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"),
            ]
        )
        products_lambda = self._build_products_lambda(role=lambda_role, props=props)
        guesty_mirror_integration = gateway.LambdaIntegration(products_lambda)
        api_v1_products_route.add_method(
            http_method="POST",
            method_responses=method_responses,
            integration=guesty_mirror_integration
        )

        api_id_convention = build_naming_convention(sufix="gw-products-api-id")
        aws_cdk.CfnOutput(
            scope=self,
            id=api_id_convention,
            export_name=api_id_convention,
            value=api.rest_api_id
        )


    def _build_products_lambda(self, role: str, props: dict) -> _lambda.Function:
        lambda_convention_name = build_naming_convention(sufix="products")
        return _lambda.DockerImageFunction(
            scope=self,
            id=lambda_convention_name,
            code=_lambda.DockerImageCode.from_image_asset(
                os.path.join(dirname, "../inline_lambdas"),
                file="./products/Dockerfile"
            ),
            role=role,
            allow_public_subnet=True,
            environment={
                "log_level": "INFO",
            },
            timeout=aws_cdk.Duration.seconds(30),
            memory_size=256
        )