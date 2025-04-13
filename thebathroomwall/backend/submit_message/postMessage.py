import json
import boto3
import uuid
import time
import html
import re

dynamodb = boto3.resource('dynamodb')
message_table = dynamodb.Table('Messages')
index_table = dynamodb.Table('MessageIndex')
ratelimit_table = dynamodb.Table('RateLimit')

# slur list
SLURS = [
    "nigger", "faggot", "cunt", "kike", "retard", "tranny", "chink", "spic",
    "dyke", "fag", "coon", "whore", "slut"
]

def sanitize_message(raw_message):
    message = html.unescape(raw_message)

    # Remove HTML tags
    message = re.sub(r'<[^>]*>', '', message)

    # Remove URLs
    message = re.sub(r'https?://\S+', '', message)      # http/https links
    message = re.sub(r'www\.\S+', '', message)          # www. links
    message = re.sub(r'\b\S+\.(com|net|org|io|gov|edu|biz|info)\b', '', message, flags=re.IGNORECASE)  # basic TLDs

    # Remove offensive slurs (case-insensitive)
    for word in SLURS:
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        message = pattern.sub('[removed]', message)

    # Strip non-printable characters and collapse whitespace
    message = re.sub(r'[^\x20-\x7E\n\t]', '', message)
    message = re.sub(r'\s{3,}', '  ', message).strip()

    return message

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        raw_message = body.get("message", "")
        sanitized = sanitize_message(raw_message)

        if not sanitized or len(sanitized) > 1000:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid message"})
            }

        headers = event.get('headers') or {}
        ip = headers.get('x-forwarded-for', '0.0.0.0').split(',')[0].strip()

        now = int(time.time())

        # Rate limit check
        response = ratelimit_table.get_item(Key={'ip': ip})
        item = response.get('Item')
        if item:
            ttl = item.get('ttl', 0)
            if ttl > now:
                retry_after = int(ttl - now)
                return {
                    "statusCode": 429,
                    "headers": { "Retry-After": str(retry_after) },
                    "body": json.dumps({
                        "error": "You're sending messages too quickly.",
                        "retry_in": retry_after,
                        "message": f"Please wait {retry_after} second(s) and try again."
                    })
                }

        # Set rate limit
        ratelimit_table.put_item(Item={
            'ip': ip,
            'ttl': now + 10
        })

        # Store the sanitized message
        message_id = str(uuid.uuid4())

        message_table.put_item(Item={
            "id": message_id,
            "message": sanitized,
            "timestamp": now
        })

        index_table.put_item(Item={
            "id": message_id
        })

        return {
            "statusCode": 200,
            "body": json.dumps({"success": True})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
