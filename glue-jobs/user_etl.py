"""
Multithreaded ETL Script for AWS Glue Job

This script performs DynamoDB scan in the main thread and
writes each batch in parallel threads for better throughput.
Optimized for I/O-bound workloads.
"""

import sys
import logging
import threading

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(threadName)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
ARG_KEYS = [
    'ENVIRONMENT',
    'SOURCE_TABLE_NAME',
    'USER_DATA_ENTRY_TABLE_NAME',
    'USER_DATA_ENTRY_VERSION_TABLE_NAME'
]


try:
    import boto3
    import botocore
except ImportError:
    logger.error("boto3 or botocore module not found. Please install them in your environment.")
    sys.exit(1)

try:
    from awsglue.utils import getResolvedOptions
except ImportError:
    logger.error("awsglue module not found. Please run this script in AWS Glue environment.")
    sys.exit(1)

try:
    args = getResolvedOptions(sys.argv, ARG_KEYS)
except KeyError as exc:
    logger.exception("Missing Glue argument: %s", exc)
    sys.exit(1)
except RuntimeError as exc:
    logger.exception("Runtime error while retrieving Glue arguments: %s", exc)
    sys.exit(1)


# DynamoDB client
dynamodb = boto3.resource('dynamodb')

source_table = dynamodb.Table(args['SOURCE_TABLE_NAME'])
target_table = dynamodb.Table(args['USER_DATA_ENTRY_TABLE_NAME'])
SCAN_LIMIT = 200
BATCH_SIZE = 25


def transform_item(item):
    """
    Map source fields to target fields. Adjust this function as needed.
    """
    if item.get('is_deployed'):
        major_version = f"{int(float(item.get('version_number')))}.0"
    else:
        major_version = item.get('version_number')

    return {
        "ddw_key": item['ddw_key'],
        "tab_name":"PI-SPI",
        "recordTypeId": item['recordTypeId'],
        "current_version": item.get('version_number'),
        "pub_version": major_version,
        "pi_term": item.get('pi_term', {}),
    }


def write_batch_thread(table_resource, items, batch_number):
    """Threaded batch writer using boto3 resource batch_writer() with composite key."""
    logger.info("⏳ Writing Batch #%d with %d items...", batch_number, len(items))
    try:
        with table_resource.batch_writer(overwrite_by_pkeys=['ddw_key', 'tab_name']) as batch:
            for item in items:
                batch.put_item(Item=item)
    except botocore.exceptions.BotoCoreError as e:
        logger.error("❌ BotoCoreError in Batch #%d: %s", batch_number, str(e))
    except botocore.exceptions.ClientError as e:
        logger.error("❌ ClientError in Batch #%d: %s", batch_number, str(e))



def scan_and_copy():
    """Scan source table and copy items to target table in batches using threads."""
    last_evaluated_key = None
    batch_number = 1
    total_copied = 0
    threads = []

    while True:
        if last_evaluated_key:
            response = source_table.scan(
                Limit=SCAN_LIMIT,
                ExclusiveStartKey=last_evaluated_key
            )
        else:
            response = source_table.scan(Limit=SCAN_LIMIT)

        items = response.get('Items', [])
        logger.info("🔍 Scanned %d items from source table.", len(items))


        # Create batches and process each in a separate thread
        for i in range(0, len(items), BATCH_SIZE):
            batch = items[i:i + BATCH_SIZE]

            transformed_data = [transform_item(item) for item in batch]

            logger.info("Data Passing: %d", len(transformed_data))

            t = threading.Thread(
                target=write_batch_thread,
                args=(target_table, transformed_data, batch_number)
            )
            t.start()
            threads.append(t)
            batch_number += 1
            total_copied += len(batch)

        last_evaluated_key = response.get('LastEvaluatedKey')
        if not last_evaluated_key:
            break

    # Wait for all threads to finish
    for t in threads:
        t.join()

    logger.info(
        "\n🎉 Done. Total %d items copied in %d batches.",
        total_copied, batch_number - 1
    )


if __name__ == "__main__":
    scan_and_copy()
