"""
This module provides an AWS Lambda function to delete a user from a DynamoDB table.
Functions:
    lambda_handler(event: dict, _context: dict) -> dict:
        Handles Lambda events to delete a user by ID from the DynamoDB table specified by the TABLE_NAME environment variable.
Environment Variables:
    TABLE_NAME: The name of the DynamoDB table from which users will be deleted.
"""
import os
import boto3


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event: dict, _context: dict) -> dict:
    """
    AWS Lambda handler to delete a user from DynamoDB table.

    Args:
        event (dict): Lambda event payload.
        _context (dict): Lambda context object (unused).

    Returns:
        dict: HTTP response with status code.
    """
    user_id = event['pathParameters']['id']
    print(f"Deleting user with ID: {user_id}")
    table.delete_item(Key={'id': user_id})
    return {'statusCode': 204}
