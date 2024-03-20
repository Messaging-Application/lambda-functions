import boto3
import json
from datetime import datetime

print('Loading function')
dynamodb = boto3.resource('dynamodb')

table_name = 'user-connections'
user_connections = dynamodb.Table(table_name)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    '''
    #print("Received event: " + json.dumps(event, indent=2))
    
    connection_id = event['requestContext']['connectionId']
    user_id = event['queryStringParameters']['userId']
    timestamp = datetime.utcnow().isoformat()

    response = user_connections.put_item(
         Item={
            'userId': user_id,  # Partition key
            'connectionString': connection_id,  # Sort key
            'timestamp': timestamp,  # Additional attribute
            
        }
        )

    return {
        'statusCode': 200,
        'body': 'Connection saved successfully'
    }
    
