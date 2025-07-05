import json
import os
import uuid
import time
import asyncio
import aioboto3

# Table name from environment
TABLE_NAME = os.environ['TABLE_NAME']

# Split data into chunks
def chunk_data(data, batch_size=10):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

# Async worker function to write a batch to DynamoDB
async def insert_batch(batch, batch_id):
    start_time = time.time()
    try:
        session = aioboto3.Session()
        async with session.resource('dynamodb') as dynamodb:
            table = await dynamodb.Table(TABLE_NAME)
            async with table.batch_writer() as writer:
                for item in batch:
                    if "id" not in item:
                        item["id"] = str(uuid.uuid4())
                    await writer.put_item(Item=item)

        duration = time.time() - start_time
        return {
            "batch_id": batch_id,
            "count": len(batch),
            "duration": round(duration, 2),
            "status": "success"
        }
    except Exception as e:
        return {
            "batch_id": batch_id,
            "error": str(e)
        }

# Async entry point
async def process_all_batches(items):
    tasks = [
        insert_batch(batch, i + 1)
        for i, batch in enumerate(chunk_data(items, batch_size=10))
    ]
    return await asyncio.gather(*tasks)

# Lambda entry point
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

        logs = asyncio.run(process_all_batches(items))

        total_time = time.time() - lambda_start
        print(f"⏱️ Lambda total time taken: {round(total_time, 2)} seconds.")
        for log in logs:
            print(f"🧩 Async Batch Log: {json.dumps(log)}")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": "All items processed using asyncio",
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
