from aws_cdk import (
    Stage,
    Environment
)
from constructs import Construct

from products_stack.products_stack import ProductsStack
from conf.aws_normalize import build_naming_convention

class ProductStackStage(Stage):

    def __init__(
        self, scope: Construct,
        id: str,
        env: Environment,
        project_name: str,
        namespace: str,
        props: dict = {}
    ):
        super().__init__(scope, id, env=env)
        product_name = build_naming_convention(
            project_name=project_name,
            namespace=namespace,
            sufix="products-stage"
        )
        ProductsStack(
            scope=self,
            construct_id=product_name,
            props=props,
            project_name=project_name,
            namespace=namespace,
        )

