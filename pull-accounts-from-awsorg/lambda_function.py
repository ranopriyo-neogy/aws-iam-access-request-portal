import json
from textwrap import indent
import os
import boto3

def handler(event, context):
    """
    This function pulls all accounts present in AWS Organization
    """
    print('received event:')
    print(event)
    client = boto3.client(
    'organizations')    
    response = {}
    accounts = {}
    try:    
        paginator = client.get_paginator('list_accounts')
        page_iterator = paginator.paginate()
        for page in page_iterator:        
            for acct in page['Accounts']:
                response[acct['Id']] = acct
        """
        Pulling Data querying the org and storing them in accounts dictionary
        """
        for id in response:
            account_name   = response[id]["Name"]
            account_id   = response[id]["Id"]
            accounts.update({account_id:account_name})
        return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(accounts,indent=4)
        }
    except Exception as e:
        print(e)
