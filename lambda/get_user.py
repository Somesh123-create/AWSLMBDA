import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    user_id = event['pathParameters']['id']
    print(f"Retrieving user with ID: {user_id}")
    response = table.get_item(Key={'id': user_id})
    item = response.get('Item')
    if item:
        return {'statusCode': 200, 'body': json.dumps(item)}
    else:
        return {'statusCode': 404, 'body': json.dumps({'error': 'User not found'})}
