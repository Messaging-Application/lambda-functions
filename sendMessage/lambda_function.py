import json
import boto3

dynamodb = boto3.resource("dynamodb")
api_gateway = boto3.client("apigateway")
sns = boto3.client('sns')

sns_topic_arn = 'arn:aws:sns:eu-central-1:569076552881:messageTopic'
table_name = "user-connections"

connection_table = dynamodb.Table(table_name)
api_gateway_endpoint = 'https://2ezs7zsjrl.execute-api.eu-central-1.amazonaws.com/prod/'  # Replace with your actual endpoint
api_gateway = boto3.client('apigatewaymanagementapi', endpoint_url=api_gateway_endpoint)

def lambda_handler(event, context):
    
    try:
        message = event['message']
        receiver_id = event['receiver_id']
        sender_id = event['sender_id']  
        chat_id = event['chat_id']
        
        message_to_send = {
        "chat_id": chat_id,
        "receiver_id": receiver_id,
        "sender_id": sender_id,
        "message_content": message
        }
        
        message_json = json.dumps(message_to_send)
        

        # Retrieve receiver's connection data
        receiver_response = connection_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(receiver_id)
        )
        receiver_items = receiver_response.get('Items', [])
        
        if receiver_items:
            receiver_connection_data = receiver_items[0]
        else:
            return {
                'statusCode': 404,
                'body': 'Receiver not found'
            }
        
        receiver_connection_string = receiver_connection_data['connectionString']
        
        # Send message to the receiver
        api_gateway.post_to_connection(
            ConnectionId=receiver_connection_string,
            Data=json.dumps({'message': message, 'sender_id': sender_id, 'receiver_id': receiver_id}).encode('utf-8')
        )
        
        # Retrieve sender's connection data
        sender_response = connection_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(sender_id)
        )
        sender_items = sender_response.get('Items', [])
        
        if sender_items:
            sender_connection_data = sender_items[0]
        else:
            return {
                'statusCode': 404,
                'body': 'Sender not found'
            }
        
        sender_connection_string = sender_connection_data['connectionString']
        
        # Send message to the sender
        api_gateway.post_to_connection(
            ConnectionId=sender_connection_string,
            Data=json.dumps({'message': message, 'sender_id': sender_id, 'receiver_id': receiver_id}).encode('utf-8')
        )
        
        message_json = json.dumps(message_to_send)
        
        response = sns.publish(
            TopicArn=sns_topic_arn,
            Message=message_json
        )
        
        print("Response from publish: ", response)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Message sent to receiver and sender')
        }
        
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': 'Unexpected error occurred'
        }