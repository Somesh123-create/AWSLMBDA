"""
Lambda function to create a user in DynamoDB.

This function expects a JSON body with 'name' and 'email' fields.
"""

import json
import os
import uuid
import boto3
from decimal import Decimal
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


def lambda_handler(event: dict, _context: dict) -> dict:
    """
    Handles the creation of a user in DynamoDB.

    Args:
        event (dict): The event dict containing the request body.
        _context (dict): The Lambda context object (unused).

    Returns:
        dict: HTTP response with status code and body.
    """
    try:
        body = json.loads(event['body'])

        # if 'name' not in body or 'email' not in body:
        #     return {
        #         'statusCode': 400,
        #         'body': json.dumps({'error': 'Missing name or email'})
        #     }
        
        # user_id = str(uuid.uuid4())
        # print(f"Creating user with ID: {user_id}")

        # item = {
        #     'id': user_id,
        #     'name': body['name'],
        #     'email': body['email'],
        # }

        # table.put_item(Item=item)
        
        item = {
            "userId": "user_123",
            "recordTypeId": "ORDER#A987",
            "orderId": "A987",
            "createdAt": "2025-07-01T13:15:00Z",
            "status": "SHIPPED",
            "shippingAddress": {
                "line1": "123 Main St",
                "city": "Bangalore",
                "pincode": "560001",
                "country": "India"
            },
            "items": [
                {
                    "productId": "P123",
                    "name": "MacBook Pro",
                    "price": Decimal("199.99"),
                    "quantity": 1
                },
                {
                    "productId": "P456",
                    "name": "USB-C Cable",
                    "price": Decimal("49.99"),
                    "quantity": 1
                }
            ],
            "paymentInfo": {
                "paymentId": "PAY999",
                "method": "CreditCard",
                "status": "Completed"
            }
        }

        # Insert the item
        table.put_item(Item=item)

        return {
            'statusCode': 201,
            'body': json.dumps(item)
        }

    except (json.JSONDecodeError, ClientError) as error:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(error)})
        }
