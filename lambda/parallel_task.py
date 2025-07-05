import json
import os
import uuid
import threading
import time
import boto3

# DynamoDB table setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])  # Set this in Lambda environment

# Split data into chunks
def chunk_data(data, batch_size=10):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

# Thread-safe print lock
print_lock = threading.Lock()

# Insert a batch of items into DynamoDB with logging
def insert_batch(batch, thread_id):
    start_time = time.time()
    with table.batch_writer() as writer:
        for item in batch:
            if "id" not in item:
                item["id"] = str(uuid.uuid4())
            writer.put_item(Item=item)

    duration = time.time() - start_time
    with print_lock:
        print(f"🧵 Thread {thread_id} inserted {len(batch)} items in {duration:.2f} seconds.")
        print(f"🧵 Thread {thread_id} data: {json.dumps(batch)}")

# Lambda handler
def lambda_handler(event, _context):
    try:
        lambda_start = time.time()

        # Parse input
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        items = body.get("users", [])

        if not isinstance(items, list) or not items:
            return {
                "statusCode": 400,
                "body": json.dumps("Missing or invalid 'users' list")
            }

        #Create and start threads for each batch
        threads = []
        for i, batch in enumerate(chunk_data(items, batch_size=10)):
            thread = threading.Thread(target=insert_batch, args=(batch, i + 1), name=f"BatchThread-{i+1}")
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        total_time = time.time() - lambda_start
        print(f"⏱️ Lambda total time taken: {total_time:.2f} seconds.")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps("All items inserted successfully.")
        }

    except Exception as e:
        print("❌ Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error: {str(e)}")
        }
