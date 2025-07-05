"""
This module defines an AWS Lambda function to retrieve a user by ID from a DynamoDB table.
Functions:
    lambda_handler(event: dict, _context: dict) -> dict:
        Handles incoming Lambda events, extracts the user ID from the path parameters,
        queries the specified DynamoDB table for the user, and returns the user data
        or an appropriate error response.
Environment Variables:
    TABLE_NAME: The name of the DynamoDB table to query.
Dependencies:
    - boto3
    - botocore.exceptions
    - os
    - json
"""
import json
import os
import requests
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from mylib.utils import my_function
import threading
from queue import Queue


def lambda_handler(event: dict, _context: dict) -> dict:
    """
    AWS Lambda handler to get a user by ID from DynamoDB.
    """
    _thread = []
    output_queue = Queue()
    

    my_number = [i for i in range(2, 101, 2)]
    
    for num in my_number:
        thread = threading.Thread(target=my_function, args=(num, output_queue))
        _thread.append(thread)
        thread.start()
        
    for thread in _thread:
        thread.join()
    
    thread_results = []
    while not output_queue.empty():
        num, result = output_queue.get()
        print(f"Finished processing number {num}, result: {result}")
        thread_results.append((num, result))
        
    print(f"Thread results: {thread_results}")

    try:
        table_name = os.environ['TABLE_NAME']
    except KeyError:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'TABLE_NAME environment variable not set'}),
            'headers': {'Content-Type': 'application/json'}
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    user_id = event.get('pathParameters', {}).get('id')
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'User ID is required'}),
            'headers': {'Content-Type': 'application/json'}
        }

    try:
        response = table.get_item(Key={'id': user_id})
        item = response.get('Item')
        if item:
            return {
                'statusCode': 200,
                'body': json.dumps(item),
                'headers': {'Content-Type': 'application/json'}
            }
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'User not found'}),
            'headers': {'Content-Type': 'application/json'}
        }
    except (BotoCoreError, ClientError) as exc:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(exc)}),
            'headers': {'Content-Type': 'application/json'}
        }
