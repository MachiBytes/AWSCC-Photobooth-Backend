"""
Takes in requestId only as parameter. Gets the whole request data and sends an email to all clients.
"""

import os
import json
import boto3

ses = boto3.client("ses")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE"])


def send_email(event_body):
    item = table.get_item(Key={"requestId": event_body["requestId"]})["Item"]
    image_path = item["imagePath"]  # templated_photos/{folder_name}
    s3_domain = f"https://awscc-photobooth-app.s3.ap-southeast-1.amazonaws.com/{image_path}"
    template_data = {
        "image1": f"{s3_domain}/1.png",
        "image2": f"{s3_domain}/2.png",
        "image3": f"{s3_domain}/3.png",
    }

    for email in item["emails"]:
        ses.send_templated_email(
            Source="awsusergroup.philippines@gmail.com",
            Destination={
                "ToAddresses": [email],
                "BccAddresses": ["markachilesflores2004@gmail.com", "awsusergroup.philippines@gmail.com"],
            },
            ReplyToAddresses=["markachilesflores2004@gmail.com", "awsusergroup.philippines@gmail.com"],
            Template="Public-Day-Sector-PH",
            TemplateData=json.dumps(template_data),
        )


def update_status(event_body):
    request_id = event_body["requestId"]
    item = table.get_item(Key={"requestId": request_id})["Item"]
    item["status"] = "sent"
    table.put_item(Item=item)


def handler(event, context):
    event_body = json.loads(event.get("body"))

    send_email(event_body)

    update_status(event_body)

    body = {
        "message": "Email sent successfully!",
        "event": event_body,
    }
    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # This allows CORS from any origin
        },
        "body": json.dumps(body),
    }
    return response
