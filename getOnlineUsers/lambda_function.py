import boto3

def lambda_handler(event, context):
    # Initialize DynamoDB client
    dynamodb = boto3.client('dynamodb')
    
    table_name = "user-connections"
    connection_table = dynamodb.Table(table_name)
    api_gateway_endpoint = 'https://2ezs7zsjrl.execute-api.eu-central-1.amazonaws.com/production/'  # Replace with your actual endpoint
    api_gateway = boto3.client('apigatewaymanagementapi', endpoint_url=api_gateway_endpoint)
    response = dynamodb.scan(TableName=table_name)

    # Filter out online users
    online_users = [user['userId']['S'] for user in response['Items']]
    
    sender_id = event['sender_id']  
    print(sender_id)

    sender_response = connection_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(sender_id)
    )
    sender_items = sender_response.get('Items', [])
    print(sender_items)
    if sender_items:
        sender_connection_data = sender_items[0]
    else:
        return {
            'statusCode': 404,
            'body': 'Sender not found'
        }
        
    sender_connection_string = sender_connection_data['connectionString']
        
    # Send message to the se
    api_gateway.post_to_connection(
        ConnectionId=sender_connection_string,
        Data=json.dumps({'action': 'updateOnlineUsers','online_user_ids': online_users}).encode('utf-8')

    return {
        'statusCode': 200
    }
