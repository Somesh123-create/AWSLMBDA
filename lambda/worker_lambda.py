"""
this module defines a Lambda function that processes messages from an SQS queue and inserts user data into a DynamoDB table.
this is SQL lambda worker that processes messages from an SQS queue and inserts user data into a DynamoDB table.
"""
import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, _context):
    """defines the Lambda function to process SQS messages and insert users into DynamoDB."""
    print(event)
    for record in event['Records']:
        try:
            users = json.loads(record['body'])
            # Insert each user
            with table.batch_writer() as batch:
                for user in users:
                    batch.put_item(Item=user)

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except boto3.exceptions.Boto3Error as e:
            print(f"Boto3 error: {e}")
        except KeyError as e:
            print(f"Missing expected key: {e}")
        except TypeError as e:
            print(f"Type error: {e}")