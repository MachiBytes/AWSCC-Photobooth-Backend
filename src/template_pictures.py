"""
Accepts a folder name and iterates over all files in that folder, puts it in a template, and uploads them to the appropriate S3 folder.

Process
1. Access the template from S3 and read as a string
2. Access the folder of raw images from S3 (name of folder passed through payload)
3. Do the templating
4. Uplaod to S3
"""

import os
import json
import boto3
import requests
from PIL import Image
from io import BytesIO

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE"])
lambda_client = boto3.client("lambda")


def template_image(event_body):
    folder_name = event_body["folderName"]
    FRAME_URL = "https://awscc-photobooth-app.s3.ap-southeast-1.amazonaws.com/assets/PSD-frame.png"
    BUCKET_URL = "https://awscc-photobooth-app.s3.ap-southeast-1.amazonaws.com"

    template = Image.open(BytesIO(requests.get(FRAME_URL).content))

    response = s3.list_objects_v2(Bucket="awscc-photobooth-app", Prefix=f"raw_photos/{folder_name}")
    image_keys = [image for image in response["Contents"] if image["Key"] != f"raw_photos/{folder_name}/"]
    offset = (350, 175)
    image_resize = (3000, 2000)

    for index, image in enumerate(image_keys):
        file_name = f"/tmp/{index+1}.png"
        image = Image.open(BytesIO(requests.get(f"{BUCKET_URL}/{image['Key']}").content))
        image = image.resize(image_resize)
        template.paste(image, offset)
        template.save(file_name)
        s3.upload_file(Filename=file_name, Bucket=os.environ["BUCKET"], Key=f"templated_photos/{folder_name}/{file_name[5:]}")
        os.remove(file_name)


def update_status(event_body):
    request_id = event_body["requestId"]
    folder_name = event_body["folderName"]
    item = table.get_item(Key={"requestId": request_id})["Item"]
    item["status"] = "templated"
    item["imagePath"] = f"templated_photos/{folder_name}"
    table.put_item(Item=item)


def handler(event, context):
    event_body = json.loads(event.get("body"))

    # Template and upload the templated image to S3
    template_image(event_body)

    # Update status in DynamoDb
    update_status(event_body)

    # Invoke send_email lambda function
    # lambda_client.invoke(
    #     FunctionName="send_email",
    #     InvocationType="Event",
    #     Payload=json.dumps({"requestId": event_body["requestId"]})
    # )

    body = {
        "message": "Image successfully templated and uploaded",
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
