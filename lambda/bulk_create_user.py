"""Lambda function to bulk create users in DynamoDB."""
import json
import uuid
import os
import boto3


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, _context):
    """Handle bulk user creation from API Gateway event."""
    try:
        body = json.loads(event['body'])
        print("Received body:", body)
        users = body.get('users', [])
        if not isinstance(users, list):
            print("Validation failed: 'users' is not a list")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "'users' must be a list"})
            }

        created_users = []
        for idx, user in enumerate(users):
            print(f"Validating user at index {idx}: {user}")
            name = user.get('name')
            email = user.get('email')

            if not name or not isinstance(name, str):
                print(f"Validation failed: Missing or invalid 'name' for user at index {idx}")
                continue
            if not email or not isinstance(email, str) or '@' not in email:
                print(f"Validation failed: Missing or invalid 'email' for user at index {idx}")
                continue

            user_id = str(uuid.uuid4())
            print(f"Creating user with ID: {user_id}")
            item = {
                'id': user_id,
                'name': name,
                'email': email,
            }
            table.put_item(Item=item)
            created_users.append(item)

        print(f"Created users: {created_users}")
        return {
            'statusCode': 201,
            'body': json.dumps({'created_users': created_users})
        }
    except (json.JSONDecodeError, KeyError, boto3.exceptions.Boto3Error) as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
