import json
import boto3
import random

dynamodb = boto3.resource('dynamodb')
message_table = dynamodb.Table('Messages')
index_table = dynamodb.Table('MessageIndex')

def lambda_handler(event, context):
    try:
        # Get all message IDs from the index
        items = []
        response = index_table.scan(ProjectionExpression="id")
        items.extend(response.get('Items', []))

        while 'LastEvaluatedKey' in response:
            response = index_table.scan(
                ProjectionExpression="id",
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))

        if not items:
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "No messages yet!"})
            }

        # Pick random ID and get the full message
        random_id = random.choice(items)["id"]
        message_item = message_table.get_item(Key={"id": random_id}).get("Item")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": message_item.get("message", "Unknown")
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
