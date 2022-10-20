import os

from aws_cdk import (
    RemovalPolicy,
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_apigateway as gateway,
    aws_dynamodb as dynamodb
)
import aws_cdk
from constructs import Construct

from conf.aws_normalize import build_naming_convention


dirname = os.path.dirname(__file__)

class ProductsStack(Stack):

    def __init__(
        self, scope: Construct,
        construct_id: str,
        props,
        project_name: str,
        namespace: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_role_convention_name = build_naming_convention(
            project_name="lambda-role",
            namespace=namespace,
            sufix="lambda-role",
        )
        policies = [
            iam.ManagedPolicy \
                .from_aws_managed_policy_name("SecretsManagerReadWrite"),
            iam.ManagedPolicy \
                .from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
            iam.ManagedPolicy \
                .from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"),
        ]
        lambda_role = iam.Role(
            scope=self,
            id=lambda_role_convention_name,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=policies
        )
        products_lambda = self._build_products_lambda(
            role=lambda_role, namespace=namespace
        )

        api_gateway_convention = build_naming_convention(
            project_name=project_name,
            namespace=namespace,
            sufix="gw-products",
        )
        api = gateway.LambdaRestApi(
            scope=self,
            id=api_gateway_convention,
            rest_api_name=api_gateway_convention,
            api_key_source_type=gateway.ApiKeySourceType.HEADER,
            default_cors_preflight_options={
                "allow_origins": gateway.Cors.ALL_ORIGINS,
                "allow_methods": gateway.Cors.ALL_METHODS
            },
            proxy=True,
            handler=products_lambda
        )
        api_id_convention = build_naming_convention(
            project_name="gw-products-api-id",
            namespace=namespace,
            sufix="gw-products-api-id",
            )
        aws_cdk.CfnOutput(
            scope=self,
            id=api_id_convention,
            export_name=api_id_convention,
            value=api.rest_api_id
        )

        # Tables
        users_table_name = build_naming_convention(
            project_name=project_name,
            namespace=namespace,
            sufix="users-tablee"
        )
        users_table = dynamodb.Table(
            scope=self,
            id=users_table_name,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            table_name="Users",
            removal_policy=RemovalPolicy.DESTROY,
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
        )
        users_table.add_global_secondary_index(
            index_name="email_gsi",
            partition_key=dynamodb.Attribute(name="email", type=dynamodb.AttributeType.STRING),
        )
        users_table.grant_read_write_data(products_lambda)
        users_table.grant_full_access(products_lambda)

        # products
        products_table_name = build_naming_convention(
            project_name=project_name,
            namespace=namespace,
            sufix="products-tablee"
        )
        products_table = dynamodb.Table(
            scope=self,
            id=products_table_name,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            table_name="Products",
            removal_policy=RemovalPolicy.DESTROY,
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
        )
        products_table.add_global_secondary_index(
            index_name="sku_gsi",
            partition_key=dynamodb.Attribute(name="sku", type=dynamodb.AttributeType.STRING),
        )
        products_table.grant_read_write_data(products_lambda)
        products_table.grant_full_access(products_lambda)


    def _build_products_lambda(
        self, role: str, namespace
    ) -> _lambda.Function:
        lambda_convention_name = build_naming_convention(
            project_name="products",
            namespace=namespace,
            sufix="products",
            )
        return _lambda.DockerImageFunction(
            scope=self,
            id=lambda_convention_name,
            code=_lambda.DockerImageCode.from_image_asset(
                os.path.join(dirname, "../../src"),
                file="./lambdas/Dockerfile"
            ),
            role=role,
            allow_public_subnet=True,
            environment={
                "log_level": "INFO",
            },
            timeout=aws_cdk.Duration.seconds(30),
            memory_size=256
        )