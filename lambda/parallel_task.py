"""
This Lambda function processes a list of user records in parallel, inserting them into a DynamoDB table in batches.
It uses threading to handle multiple batches concurrently, improving performance for large datasets.
"""

import json
import os
import uuid
import threading
import boto3

# DynamoDB table setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])  # Set this in Lambda environment


def chunk_data(data, batch_size=10):
    """Splits the input data into chunks of specified batch size."""
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

def insert_batch(batch):
    """Inserts a batch of items into the DynamoDB table."""
    with table.batch_writer() as writer:
        for item in batch:
            if "id" not in item:
                item["id"] = str(uuid.uuid4())
            writer.put_item(Item=item)
    print(f"✅ Inserted batch of {len(batch)} items.")


def lambda_handler(event, _context):
    """AWS Lambda handler to process user records in parallel."""
    try:
        # Parse body
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        items = body.get("users", [])

        if not isinstance(items, list) or not items:
            return {
                "statusCode": 400,
                "body": json.dumps("Missing or invalid 'users' list")
            }

        # Split into batches of 10 and use threading
        threads = []
        for batch in chunk_data(items, batch_size=10):
            thread = threading.Thread(target=insert_batch, args=(batch,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps("All items inserted successfully.")
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error: {str(e)}")
        }
