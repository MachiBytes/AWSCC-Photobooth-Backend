import json


def handler(event, context):
    """
    Register new admins to the database.

    Resources:
    - DynamoDB

    Payload:
    - username: str
    - password: str, SHA256 encoded

    Database schema
    - username: str
    - password: str, SHA256 encoded
    - last_logged_in: datetime
    """

    try:
        event_body = json.loads(event.get("body"))

        #

        status_code = 200
        message = "Successful."
    except Exception as e:
        status_code = 400
        message = "An error occured. " + e

    body = {
        "message": message,
        "event": event,
    }
    response = {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # This allows CORS from any origin
        },
        "body": json.dumps(body),
    }
    return response
