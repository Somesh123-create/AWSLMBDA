import json
import boto3
import os
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    body = json.loads(event['body'])
    user_id = str(uuid.uuid4())
    item = {
        'id': user_id,
        'name': body.get('name'),
        'email': body.get('email'),
    }
    table.put_item(Item=item)
    return {
        'statusCode': 201,
        'body': json.dumps(item)
    }
