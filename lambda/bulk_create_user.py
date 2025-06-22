"""Lambda function to bulk create users in DynamoDB."""
import json
import uuid
import os
import boto3
from botocore.exceptions import BotoCoreError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

sqs = boto3.client('sqs')
QUEUE_URL = os.environ['QUEUE_URL']

def lambda_handler(event: dict, _context: dict) -> dict:
    """Handle bulk user creation from API Gateway event."""
    try:
        body = json.loads(event['body'])
        users = body.get('users', [])
        # Validate and add IDs
        valid_users = [
            {
                "id": str(uuid.uuid4()),
                "name": user["name"],
                "email": user["email"]
            }
            for user in users
            if isinstance(user.get("name"), str) and "@" in user.get("email", "")
        ]

        # Send one message with all users
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(valid_users)
        )

        return {
            "statusCode": 202,
            "body": json.dumps({"message": f"{len(valid_users)} users queued for background processing"})
        }
    except (json.JSONDecodeError, KeyError, BotoCoreError) as exc:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(exc)})
        }
