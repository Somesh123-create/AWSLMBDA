"""
This module provides an AWS Lambda function to delete a user from a DynamoDB table.
Functions:
    lambda_handler(event: dict, _context: dict) -> dict:
        Handles Lambda events to delete a user by ID from the DynamoDB table specified by the TABLE_NAME environment variable.
Environment Variables:
    TABLE_NAME: The name of the DynamoDB table from which users will be deleted.
"""
import os
from multiprocessing import Process, Pipe
from mylib.utils import my_function_ml_procs
import boto3


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])



def run_parallel_with_processes(numbers: list) -> list:
    processes = []
    conns = []

    print(f"Creating {len(numbers)} processes...")

    for num in numbers:
        parent_conn, child_conn = Pipe()
        p = Process(target=my_function_ml_procs, args=(num, child_conn))
        processes.append((p, parent_conn))
        conns.append(parent_conn)
        p.start()

    results = []

    for (p, conn) in processes:
        p.join(timeout=30)  # wait 30 seconds
        if p.is_alive():
            p.terminate()
            results.append({"error": f"Process {p.pid} timed out"})
        else:
            try:
                if conn.poll():
                    results.append(conn.recv())
                else:
                    results.append({"error": f"No data received from process {p.pid}"})
            except Exception as e:
                results.append({"error": f"Exception while receiving from process {p.pid}: {str(e)}"})
        conn.close()

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
