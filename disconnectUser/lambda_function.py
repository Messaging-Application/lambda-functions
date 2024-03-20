import json
import boto3

dynamodb = boto3.resource('dynamodb')

table_name = 'user-connections'
user_connections = dynamodb.Table(table_name)

def lambda_handler(event, context):
    print("event as follows: ", event)
    
    connection_id = event['requestContext']['connectionId']
    
    # Query the table using the GSI to find the userId associated with the connectionId
    try:
        response = user_connections.query(
            IndexName='connectionString-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('connectionString').eq(connection_id)
        )
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': 'Error when Querying'
        }
    
    print('Response: ', response)
    
    if response['Items']:
        # Assuming each connectionId is unique, there should only be one item
        user_id = response['Items'][0]['userId']
    # Delete the item from the DynamoDB table
    
    print('userId: ', user_id)
    print('connection_id: ', connection_id)
    try:
        response = user_connections.delete_item(
            Key={
                'userId': user_id,
                'connectionString': connection_id
            }
        )
        # You can include additional parameters as needed, for example:
        # ConditionExpression, ExpressionAttributeValues, ReturnValues, etc.
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': 'Error deleting item from DynamoDB'
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps('User disconnected with success!')
    }
