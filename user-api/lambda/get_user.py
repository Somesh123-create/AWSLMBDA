import json
import boto3
import os

dynamo = boto3.resource('dynamodb')
table = dynamo.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    user_id = event['pathParameters']['id']
    response = table.get_item(Key={'id': user_id})
    item = response.get('Item')
    if item:
        return {"statusCode": 200, "body": json.dumps(item)}
    else:
        return {"statusCode": 404, "body": json.dumps({"error": "User not found"})}
