from src.utils import http as http_utils
from src.utils import logger as _logger

logger = _logger.get_logger()


def main(event, context):
    logger.info("hello world.")
    http_utils.response_success(data={"msg": "ok"})
