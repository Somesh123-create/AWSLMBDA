"""
Multithreaded ETL Script for AWS Glue Job

This script performs parallel ETL operations using threading within a single Glue worker node.
It is optimized for I/O-bound workloads (e.g., S3 operations, lightweight transformation).
"""

import sys
import time
import boto3
import logging
import threading
from awsglue.utils import getResolvedOptions

# DynamoDB client
dynamodb = boto3.client('dynamodb')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(threadName)s: %(message)s"
)
logger = logging.getLogger(__name__)


# Constants
NUM_WORKER_THREADS = 5
ARG_KEYS = ['ENVIRONMENT', 'SOURCE_TABLE_NAME', 'USER_DATA_ENTRY_TABLE_NAME', 'USER_DATA_ENTRY_VERSION_TABLE_NAME']


try:
    args = getResolvedOptions(sys.argv, ARG_KEYS)
except ImportError as e:
    logger.exception("AWS Glue modules could not be imported. Are you running this outside Glue?")
    sys.exit(1)
except Exception as e:
    logger.exception("Failed to parse required Glue job arguments.")
    sys.exit(1)

SOURCE_TABLE = args['SOURCE_TABLE_NAME']
TARGET_TABLE_MAIN = args['USER_DATA_ENTRY_TABLE_NAME']
TARGET_TABLE_VERSION = args['USER_DATA_ENTRY_VERSION_TABLE_NAME']
SCAN_LIMIT = 200  # Fetch 1000 items at a time
BATCH_SIZE = 25    # DynamoDB batch write limit


logger.info(f"SOURCE_TABLE: {SOURCE_TABLE}, TARGET_TABLE_MAIN: {TARGET_TABLE_MAIN}, TARGET_TABLE_VERSION: {TARGET_TABLE_VERSION}, SCAN_LIMIT: {SCAN_LIMIT}")


scan_args = {
    'TableName': SOURCE_TABLE,
    'Limit': SCAN_LIMIT
}

response = dynamodb.scan(**scan_args)

items = response.get('Items', [])
print(f"\n🔍 Scanned {len(items)} items from source table.")
