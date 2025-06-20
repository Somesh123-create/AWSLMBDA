import json
import boto3
import os

dynamo = boto3.resource('dynamodb')
table = dynamo.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    user_id = event['pathParameters']['id']
    table.delete_item(Key={'id': user_id})
    return {"statusCode": 204}
