import json
import boto3


def lambda_handler(event, context):
    user_id = event["headers"]["user_id"].strip()

    location = get_location_from_s3(str(user_id))

    return {
        'statusCode': 200,
        'body': location
    }


def get_location_from_s3(user_id):
    client = boto3.client('s3')

    response = client.get_object(
        Bucket='magic-clock-user-location',
        Key=user_id,
    )

    response_text = response["Body"].read()

    return response_text
