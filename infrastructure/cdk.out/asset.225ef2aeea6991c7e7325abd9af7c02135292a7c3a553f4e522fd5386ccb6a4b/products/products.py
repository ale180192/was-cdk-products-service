import email
import boto3
from uuid import uuid4

from src.utils import http as http_utils
from src.utils import logger as _logger

logger = _logger.get_logger()


def main(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("users")
    table.put_item(Item={"id": uuid4().hex, "email": "test@email.com"})
    return http_utils.response_success(data={"msg": "ok"})
