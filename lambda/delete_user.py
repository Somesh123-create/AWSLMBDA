"""
This module provides an AWS Lambda function to delete a user from a DynamoDB table.
Functions:
    lambda_handler(event: dict, _context: dict) -> dict:
        Handles Lambda events to delete a user by ID from the DynamoDB table specified by the TABLE_NAME environment variable.
Environment Variables:
    TABLE_NAME: The name of the DynamoDB table from which users will be deleted.
"""
import os
from multiprocessing import Process, Queue, cpu_count
from mylib.utils import my_function
import boto3


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])



def run_parallel_with_processes(numbers: list) -> list:
    processes = []
    output_queue = Queue()

    max_workers = min(len(numbers), cpu_count())
    print(f"Using up to {max_workers} processes.")

    for num in numbers:
        p = Process(target=my_function, args=(num, output_queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    results = []
    while not output_queue.empty():
        results.append(output_queue.get())

    return results


def lambda_handler(event: dict, _context: dict) -> dict:
    """
    AWS Lambda handler to delete a user from DynamoDB table.

    Args:
        event (dict): Lambda event payload.
        _context (dict): Lambda context object (unused).

    Returns:
        dict: HTTP response with status code.
    """
    
    my_numbers = list(range(2, 101, 2))
    
    try:
        process_results = run_parallel_with_processes(my_numbers)
        print(f"Process results: {process_results}")
    except Exception as e:
        print(f"Error in multiprocessing: {e}")
        process_results = []
    
    user_id = event['pathParameters']['id']
    print(f"Deleting user with ID: {user_id}")
    table.delete_item(Key={'id': user_id})
    return {'statusCode': 204}
