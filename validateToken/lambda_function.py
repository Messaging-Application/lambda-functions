import os
import json
import requests

def lambda_handler(event, context):
    # Retrieve the JWT token from the incoming request's cookies
    auth_header = event['headers'].get('Authorization', '')

    jwt_token = auth_header.split(' ')[1] if len(auth_header.split(' ')) > 1 else auth_header
    print("JWT Token: ", jwt_token)
    
    if not jwt_token:
        print("No JWT token provided")
        return generate_deny_policy(event['methodArn'])
    
    # Prepare the request to the authentication microservice
    validate_url = os.environ['AUTH_MICROSERVICE_URL'] + '/validate'
    cookies = {os.environ['JWT_COOKIE_NAME']: jwt_token}
    print("url: ", validate_url)
    
    # Make the request to the authentication microservice
    response = requests.post(validate_url, cookies=cookies)
    print("response: ", response)
    
    if response.status_code == 200:
        # If the microservice validates the token, generate an allow policy
        return generate_allow_policy(event['methodArn'])
    else:
        # If the token is invalid or any other error occurs, generate a deny policy
        return generate_deny_policy(event['methodArn'])

def generate_allow_policy(resource):
    return generate_policy('user', 'Allow', resource)

def generate_deny_policy(resource):
    return generate_policy('user', 'Deny', resource)

def generate_policy(principal_id, effect, resource):
    # Generate an IAM policy document for API Gateway
    policy_document = {
        'Version': '2012-10-17',
        'Statement': [{
            'Action': 'execute-api:Invoke',
            'Effect': effect,
            'Resource': resource
        }]
    }
    return {
        'principalId': principal_id,
        'policyDocument': policy_document
    }
