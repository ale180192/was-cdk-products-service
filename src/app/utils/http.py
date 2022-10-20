import json

def response_success(data: dict = {}, status_code=200) -> dict:
    return {
        "statusCode": str(status_code),
        "headers": {},
        "body": json.dumps(data),
        "isBase64Encoded":  False
    }

def response_error(data: dict = {}, status_code: int = 500) -> dict:
    return {
        "statusCode": str(status_code),
        "headers": {},
        "body": json.dumps(data),
        "isBase64Encoded":  False
    } 