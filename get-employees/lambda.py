import json
import boto3

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('employees')

def lambda_handler(event, context):

    response = table.scan()

    return {

        "statusCode": 200,

        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        },

        "body": json.dumps(
            response['Items']
        )
    }
