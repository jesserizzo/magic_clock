import json
import boto3


def lambda_handler(event, context):
    user_id = event["user_id"]
    location_string = str(event["location"])
    location_bytes = location_string.encode("utf-8")
    response = put_object(str(user_id), location_bytes)

    return {
        'statusCode': 200,
        'body': response
    }


def put_object(user_id, text_bytes):
    client = boto3.client('s3')
    response = client.put_object(
        ACL='private',
        Body=text_bytes,
        Bucket='magic-clock-user-location',
        # CacheControl='string',
        ContentDisposition='text/plain',
        ContentEncoding='utf-8',
        Key=user_id,
        # Metadata={
        #     'string': 'string'
        # },
        # StorageClass='STANDARD'|'REDUCED_REDUNDANCY'|'STANDARD_IA'|'ONEZONE_IA'|'INTELLIGENT_TIERING'|'GLACIER'|'DEEP_ARCHIVE',
    )

    return response
