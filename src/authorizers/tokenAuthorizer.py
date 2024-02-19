import os
import jwt

# Encrypt AWSCLOUDCLUBPUPMANILA with SHA256
SECRET_TOKEN = os.environ["SECRET_TOKEN"]


def generate_policy(principalId, effect, resource):
    authPolicy = {
        "principalId": principalId,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource,
                }
            ],
        },
    }
    return authPolicy


def handler(event, context):
    print(event)
    token = event["headers"]["authorization"]
    try:
        print(token)
        decoded = jwt.decode(token, (SECRET_TOKEN), algorithms=["HS256"])
        authPolicy = generate_policy(decoded["sub"], "Allow", event["routeArn"])
    except Exception as e:
        print(e)
        authPolicy = generate_policy("unauthorized", "Deny", event["routeArn"])
        return authPolicy

    print("Successful!")
    print(authPolicy)
    return authPolicy
