import json
import logging
from functools import wraps
from boto3.dynamodb.types import TypeDeserializer
from contextlib import contextmanager
import inspect

# Setup basic logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize deserializer
deserializer = TypeDeserializer()


def deserialize_ddb_image(ddb_image):
    """Convert DynamoDB AttributeValue dict to Python dict."""
    return {key: deserializer.deserialize(value) for key, value in ddb_image.items()}


@contextmanager
def event_processing(event_name):
    """
    Context manager for logging the start and end of event processing.
    Args:
        event_name: The name of the DynamoDB event being processed.
    Yields:
        None
    """
    logger.info(f"Start processing event: {event_name}")
    try:
        yield
        logger.info(f"Finished processing event: {event_name}")
    except Exception as exc:
        logger.error(f"Exception during event '{event_name}': {exc}")
        raise


# Decorator to log entry and exit of the handler
def log_event_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"➡️ Entering: {func.__name__}")

        # Introspect to decide what to log
        sig = inspect.signature(func)
        param_count = len(sig.parameters)
        logger.info(f"Function signature: {sig}")
        logger.info(f"Args: {args}, Kwargs: {kwargs}")
        logger.info(f"Arguments: {[type(arg).__name__ for arg in args]}")
        logger.info(f"Keyword Arguments: {list(kwargs.keys())}")

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            logger.info(f"⬅️ Exiting: {func.__name__}")

    return wrapper


@log_event_handler
def handle_insert(record):
    """
    Handle INSERT events from DynamoDB streams.
    Args:
        record: The DynamoDB stream record for the INSERT event.
    """
    new_image = record.get('dynamodb', {}).get('NewImage', {})
    payload = {
        'eventType': 'INSERT',
        'newRecord': deserialize_ddb_image(new_image),
        'timestamp': record.get('dynamodb', {}).get('ApproximateCreationDateTime')
    }
    logger.info(json.dumps(payload, indent=2))
    add_history_record(payload)
    logger.info('Handled INSERT Event')

@log_event_handler
def handle_modify(record):
    """
    Handle MODIFY events from DynamoDB streams.
    Args:
        record: The DynamoDB stream record for the MODIFY event.
    """
    new_image = record.get('dynamodb', {}).get('NewImage', {})
    old_image = record.get('dynamodb', {}).get('OldImage', {})
    payload = {
        'eventType': 'MODIFY',
        'oldRecord': deserialize_ddb_image(old_image),
        'newRecord': deserialize_ddb_image(new_image),
        'timestamp': record.get('dynamodb', {}).get('ApproximateCreationDateTime')
    }
    logger.info(json.dumps(payload, indent=2))
    add_history_record(payload)
    logger.info('Handled MODIFY Event')

@log_event_handler
def handle_remove(record):
    """
    Handle REMOVE events from DynamoDB streams.
    Args:
        record: The DynamoDB stream record for the REMOVE event.
    """
    old_image = record.get('dynamodb', {}).get('OldImage', {})
    payload = {
        'eventType': 'REMOVE',
        'oldRecord': deserialize_ddb_image(old_image),
        'timestamp': record.get('dynamodb', {}).get('ApproximateCreationDateTime')
    }
    logger.info(json.dumps(payload, indent=2))
    add_history_record(payload)
    logger.info('Handled REMOVE Event')
 

def add_history_record(payload):
    """
    Add a history record to the new table.
    Replace this stub with actual database logic (e.g., boto3 put_item).
    Args:
        payload: The JSON-serializable payload to write to the history table.
    """
    logger.info(f"[DB] Writing history record: {json.dumps(payload)}")



# Lambda function handler with decorator
@log_event_handler
def lambda_handler(event, context):
    logger.info("📦 Received event: %s", json.dumps(event))
    logger.info('-' * 38)
    try:
        for record in event.get('Records', []):
            event_name = record.get('eventName')
            with event_processing(event_name):
                if event_name == 'INSERT':
                    handle_insert(record)
                elif event_name == 'MODIFY':
                    handle_modify(record)
                elif event_name == 'REMOVE':
                    handle_remove(record)
                else:
                    logger.warning("Event '%s' not handled", event_name)
        logger.info('-' * 38)
        return "Done"
    except Exception as e:
        logger.error("Error: %s", e)
        logger.info('-' * 38)
        return "Error"