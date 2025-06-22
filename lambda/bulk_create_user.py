"""Lambda function to bulk create users in DynamoDB."""
import json
import uuid
import os
import boto3
from botocore.exceptions import BotoCoreError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event: dict, _context: dict) -> dict:
    """Handle bulk user creation from API Gateway event."""
    try:
        body = json.loads(event['body'])
        users = body.get('users', [])
        if not isinstance(users, list):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "'users' must be a list"})
            }

        created_users = []
        for user in users:
            name = user.get('name')
            email = user.get('email')

            if not name or not isinstance(name, str):
                continue
            if not email or not isinstance(email, str) or '@' not in email:
                continue

            user_id = str(uuid.uuid4())
            item = {
                'id': user_id,
                'name': name,
                'email': email,
            }
            table.put_item(Item=item)
            created_users.append(item)

        return {
            'statusCode': 201,
            'body': json.dumps({'created_users': created_users})
        }
    except (json.JSONDecodeError, KeyError, BotoCoreError) as exc:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(exc)})
        }
