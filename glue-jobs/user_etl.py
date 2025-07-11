"""
Multithreaded ETL Script for AWS Glue Job

This script performs parallel ETL operations using threading within a single Glue worker node.
It is optimized for I/O-bound workloads (e.g., S3 operations, lightweight transformation).
"""

import sys
import time
import logging
import threading

# Constants
NUM_WORKER_THREADS = 5
ARG_KEYS = ['ENVIRONMENT', 'TABLE_NAME']

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(threadName)s: %(message)s"
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parses and returns required Glue arguments."""
    try:
        from awsglue.utils import getResolvedOptions
        args = getResolvedOptions(sys.argv, ARG_KEYS)
        return args
    except ImportError as e:
        logger.exception("AWS Glue modules could not be imported. Are you running this outside Glue?")
        sys.exit(1)
    except Exception as e:
        logger.exception("Failed to parse required Glue job arguments.")
        sys.exit(1)


def process_partition(partition_id: int):
    """
    Simulates processing for a partition or unit of work.

    Args:
        partition_id (int): Identifier for the current partition or task unit.
    """
    logger.info(f"Started processing partition {partition_id}")
    try:
        # Simulate task (replace this with actual ETL logic)
        time.sleep(2)
    except Exception as e:
        logger.error(f"Error processing partition {partition_id}: {e}")
    finally:
        logger.info(f"Finished processing partition {partition_id}")


def run_etl(args):
    """
    Coordinates the multithreaded ETL process.

    Args:
        args (dict): Parsed Glue job arguments.
    """
    logger.info("ETL job started.")
    logger.info(f"Environment: {args['ENVIRONMENT']}")
    logger.info(f"Target Table: {args['TABLE_NAME']}")
    logger.info(f"Launching {NUM_WORKER_THREADS} worker threads...")

    threads = []
    for i in range(NUM_WORKER_THREADS):
        thread = threading.Thread(target=process_partition, args=(i + 1,), name=f"Worker-{i + 1}")
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    logger.info("ETL job completed successfully.")


def main():
    args = parse_arguments()
    run_etl(args)


if __name__ == "__main__":
    main()
