import json
import boto3
import os
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    try:
        print("Received event:", event)
        body = json.loads(event.get('body', '{}'))
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
    except Exception as e:
        print(f"Error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
