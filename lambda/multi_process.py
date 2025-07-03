import json
import os
import uuid
import time
import boto3
from multiprocessing import Process, Pipe

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])  # Set in Lambda or env

# Split data into chunks
def chunk_data(data, batch_size=10):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

# Worker function run in a separate process
def insert_batch(batch, conn, process_id):
    start_time = time.time()
    try:
        with table.batch_writer() as writer:
            for item in batch:
                if "id" not in item:
                    item["id"] = str(uuid.uuid4())
                writer.put_item(Item=item)

        duration = time.time() - start_time
        log = {
            "process_id": process_id,
            "count": len(batch),
            "duration": round(duration, 2),
            "data": batch
        }
        conn.send(log)
    except Exception as e:
        conn.send({"process_id": process_id, "error": str(e)})
    finally:
        conn.close()

# Lambda handler
def lambda_handler(event, _context):
    try:
        lambda_start = time.time()

        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        items = body.get("users", [])

        if not isinstance(items, list) or not items:
            return {
                "statusCode": 400,
                "body": json.dumps("Missing or invalid 'users' list")
            }

        # Split and start processes
        processes = []
        pipes = []
        for i, batch in enumerate(chunk_data(items, batch_size=10)):
            parent_conn, child_conn = Pipe()
            p = Process(target=insert_batch, args=(batch, child_conn, i + 1))
            p.start()
            processes.append((p, parent_conn))

        logs = []

        # Join all processes and collect logs
        for p, conn in processes:
            p.join(timeout=30)
            if p.is_alive():
                p.terminate()
                logs.append({"error": f"Process {p.name} timed out"})
            elif conn.poll():
                logs.append(conn.recv())
            else:
                logs.append({"error": f"No response from {p.name}"})

        total_time = time.time() - lambda_start
        print(f"⏱️ Lambda total time taken: {round(total_time, 2)} seconds.")

        for log in logs:
            print(f"🧩 Process Log: {json.dumps(log)}")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": "All items processed (locally or EC2 only)",
                "logs": logs,
                "total_time_sec": round(total_time, 2)
            })
        }

    except Exception as e:
        print("❌ Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error: {str(e)}")
        }
