import json
import boto3

dynamodb = boto3.resource('dynamodb')
message_table = dynamodb.Table('Messages')
index_table = dynamodb.Table('MessageIndex')

def lambda_handler(event, context):
    deleted = 0
    scanned = 0

    try:
        last_key = None

        while True:
            scan_kwargs = {
                "ProjectionExpression": "id, message"
            }
            if last_key:
                scan_kwargs["ExclusiveStartKey"] = last_key

            response = message_table.scan(**scan_kwargs)
            items = response.get("Items", [])

            for item in items:
                scanned += 1
                msg = item.get("message", "")
                if "[removed]" in msg.lower():
                    message_table.delete_item(Key={"id": item["id"]})
                    index_table.delete_item(Key={"id": item["id"]})
                    deleted += 1

            last_key = response.get("LastEvaluatedKey")
            if not last_key:
                break

        return {
            "statusCode": 200,
            "body": json.dumps({
                "deleted": deleted,
                "scanned": scanned,
                "message": "Cleanup complete."
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "deleted": deleted,
                "scanned": scanned
            })
        }
