import boto3
import json
from botocore.exceptions import ClientError

def handler(event, context):
    """
    This function will pull all IAM policies from AWS Organization Main account 
    """
    try:
        policy_arn=[]
        iam = boto3.client('iam')
        paginator = iam.get_paginator('list_policies')
        response_iterator = paginator.paginate()
        for page in response_iterator:
            for index in page['Policies']:
                    if(policy_arn != "arn:aws:iam::aws:policy/AdministratorAccess"):
                        policy_arn.append(index['Arn'])
        return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(policy_arn,indent=4)
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'ServiceFailureException':
            print("Exception Occured as ServiceFailureException")