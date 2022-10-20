from typing import Any, List
import boto3
from boto3.resources.base import ServiceResource
from boto3.dynamodb.conditions import Key
from s3transfer import logger

from app.utils import get_env
from app.domain.models import (
    UserModel,
    ProductModel,
)
from app.utils.logger import get_logger

logger = get_logger()

def get_db() -> ServiceResource:
    """
    Return a dynamodb conexion depends of the env.
    When the service is running into the lambdas by
    default the secrets will be loaded to the boto3.resource()
    method
    :returns: (ServiceResource) dynamodb resource
    """
    if get_env("ENVIRONMENT") == "local":
        ddb = boto3.resource("dynamodb",
            endpoint_url="http://localhost:8000")
        client = boto3.client("dynamodb",
            endpoint_url="http://localhost:8000")

        logger.info("local environment .....")

    else:
        ddb = boto3.resource("dynamodb")
        client = boto3.client("dynamodb")

    return ddb, client

class UserRepositoryAbstract:

    def get_all(self) -> List:
        raise NotImplementedError()


    def create_user(self, id: str, email: str) -> Any:
        raise NotImplementedError()


class UsersRepository:
    def __init__(self, db: ServiceResource, client: Any) -> None:
        self._db = db
        self._client = client
        self._table_name = "Users"

    def get_all(self) -> List:
        """
        Returns all the users
        """
        table = self._db.Table(self._table_name)
        response = table.scan()             
        return response.get('Items', [])

    def get_by_email(self, email: str) -> UserModel:
        """
        Returns the user if it exists
        """
        table = self._db.Table(self._table_name)
        response = table.query(
            IndexName="email_gsi",
            KeyConditionExpression=Key("email").eq(email),
        )
        user = None
        for item in response['Items']:
            user = item
        
        return user

    def get_by_id(self, id: str) -> UserModel:
        """
        Returns the user if it exists
        """
        table = self._db.Table(self._table_name)
        user = table.get_item(Key={"id": id})
        
        return user.get("Item")

    def create(self, user: dict):
        self._client.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": self._table_name,
                        "Item": {
                            "id": { "S": f"email#{user.get('email')}" },
                        },
                        "ConditionExpression": 'attribute_not_exists(PK)'
                    }
                },
                {
                    "Put": {
                        "TableName": self._table_name,
                        "Item": {
                            "id": { "S": user.get("id") },
                            "email": {"S": user.get("email")},
                            "password": {"S": user.get("password")},
                            "first_name": {"S": user.get("first_name", False)},
                            "is_admin": {"BOOL": user.get("is_admin", False)},
                        },
                        "ConditionExpression": "attribute_not_exists(PK)"
                    }
                }
            ]
        )

        return user


class ProductRepository:
    def __init__(self, db: ServiceResource, client: Any) -> None:
        self._db = db
        self._client = client
        self._table_name = "Products"

    def get_by_id(self, id: str) -> ProductModel:
        """
        Returns the product if it exists
        """
        table = self._db.Table(self._table_name)
        product = table.get_item(Key={"id": id})
        
        return product["Item"]

    def get_all(self) -> List:
        """
        Returns all the products
        """
        table = self._db.Table(self._table_name)
        response = table.scan()             
        return response.get('Items', [])

    def get_by_sku(self, sku: str) -> ProductModel:
        """
        Returns the product if it exists
        """
        table = self._db.Table(self._table_name)
        response = table.query(
            IndexName="sku_gsi",
            KeyConditionExpression=Key("sku").eq(sku),
        )
        user = None
        for item in response['Items']:
            user = item
        
        return user

    def create(self, product: dict):
        self._client.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": self._table_name,
                        "Item": {
                            "id": { "S": f"sku#{product.get('sku')}" },
                        },
                        "ConditionExpression": 'attribute_not_exists(PK)'
                    }
                },
                {
                    "Put": {
                        "TableName": self._table_name,
                        "Item": {
                            "id": { "S": product.get("id") },
                            "sku": {"S": product.get("sku")},
                            "name": {"S": product.get("name")},
                            "price": {"S": product.get("price")},
                            "brand": {"S": product.get("brand")},
                        },
                        "ConditionExpression": "attribute_not_exists(PK)"
                    }
                }
            ]
        )

        return product

    def update_with_sku(self, id: str, product: dict, current_sku: str):
        self._client.transact_write_items(
            TransactItems=[
                {
                    "Update": {
                        "TableName": self._table_name,
                        "Key": { "id": { "S": id} },
                        "UpdateExpression": "SET sku = :sku, price = :price, brand = :brand",
                        "ExpressionAttributeValues":{
                            ":sku":{"S": product.get("sku")},
                            # ":name":{"S": product.get("name")},
                            ":price":{"S": product.get("price")},
                            ":brand":{"S": product.get("brand")},
                        }
                    }
                },
                {
                    "Delete": {
                        "TableName" : self._table_name,
                        "Key" : {"id": {"S": f"sku#{current_sku}" } }
                    }
                },
                {
                    "Put": {
                        "TableName": self._table_name,
                        "ConditionExpression": 'attribute_not_exists(PK)',
                        "Item": {
                            "id": { "S": f"sku#{product.get('sku')}" },
                        }
                    }
                }
            ]
        )
        product["id"] = id
        return product


    def update(self, id: str, product: dict):
        self._client.transact_write_items(
            TransactItems=[
                {
                    "Update": {
                        "TableName": self._table_name,
                        "Key": { "id": { "S": id} },
                        "UpdateExpression": "SET sku = :sku, price = :price, brand = :brand",
                        "ExpressionAttributeValues":{
                            ":sku":{"S": product.get("sku")},
                            # ":name":{"S": product.get("name")},
                            ":price":{"S": product.get("price")},
                            ":brand":{"S": product.get("brand")},
                        }
                    }
                }
            ]
        )
        product["id"] = id
        return product

