import json
import requests

def lambda_handler(event, context):
    # URL of your backend endpoint
    backend_url = 'http://172.31.23.233:8080/message/save-message'

    try:
        # Make a GET request to the backend URL
        print("******Calling Backend*****")
        response = requests.get(backend_url)
        
        
        # Check if the request was successful
        if response.status_code == 200:
            print('Notification sent successfully.')
        else:
            print(f'Failed to notify. Status code: {response.status_code}')
            
    except Exception as e:
        print(f'Error sending notification: {e}')
    
    return {
        'statusCode': 200,
        'body': json.dumps('Lambda executed successfully!')
    }

