"""
This Lambda function processes messages from an SQS queue in parallel.
"""
import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, _context):
    """Processes messages from SQS and inserts data into DynamoDB."""
    for record in event['Records']:
        payload = json.loads(record['body'])
        # Perform your processing logic here
        # For example, you can store the result in DynamoDB
        table.put_item(Item=payload)
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete')
    }