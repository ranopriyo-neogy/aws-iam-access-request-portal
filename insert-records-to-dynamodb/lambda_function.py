import boto3
import json
import os
import uuid
import time
import secrets
import string
from datetime import datetime

def handler(event, context):
    """
    Inserts data into DynamoDB and passes and calls fetch_arn() method for permission set arn
    """
    item = {}
    id = str(uuid.uuid1())
    item = json.loads(event['body'])
    password_update = ""
    print("Value of item:\n",item)
    item.update({'id':id, 'executionCount':'1','isApproved':'false','isdeleted':'false'})
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    item.update({'fromdate':current_time})
    for key,value in item.items(): 
        if(key == 'todate'):
            todate_formatted= str((datetime.fromisoformat(value[:-1])).strftime("%d/%m/%Y %H:%M:%S"))
            item.update({'todate':todate_formatted})
            break
    for key,value in item.items(): 
        if(key == 'accessType' and value == 'console'):
            characters = string.digits + string.ascii_letters + string.punctuation
            for i in range(20):
                password_update = password_update + secrets.choice(characters)
            item.update({'password':password_update})
            break
        if(key == 'accessType' and value == 'terminal'):
            item.update({'password':'NA'})
            break
    client_dynamo=boto3.resource('dynamodb')
    table = client_dynamo.Table('elevate-access-request')
    try:  
        json_object = json.dumps(item, indent = 4) 
        response = table.put_item(Item=json.loads(json_object))
        print(json_object)
        print(response)
  
        return {
        'statusCode': 200,
        'headers': {
          'Access-Control-Allow-Headers': '*',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('Hello from your new Amplify Python lambda!')
        }
    except:
        raise