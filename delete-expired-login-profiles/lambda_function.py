import boto3;
import os;
import time;
from botocore.exceptions import ClientError;
from datetime import datetime

def lambda_handler(event,context):
    """
    This method scan the DynamoDB and fetches user details in a dictionary where current date is greater than end date 
    This further passes the dict to the dettach_permissions() method
    """
    expired_perms_terminal={}
    expired_perms_console={}
    count_console=0
    count_terminal=0
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('elevate-access-request')
    response = table.scan()
    data = response
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response)
    current_time = datetime.now()
    for i in data['Items']:
        if(current_time>datetime.strptime(i['todate'], '%d/%m/%Y %H:%M:%S') and i['isdeleted']=='false' and i['isApproved']=='true' and i['accessType']=='console'):
            count_console = count_console+1
            expired_perms_console[count_console]={'id':i['id'],'user':i['user'],'accessType':i['accessType'],'account_id':i['account_id'],'policy_arn':i['policy_arn']}
        if(current_time>datetime.strptime(i['todate'], '%d/%m/%Y %H:%M:%S') and i['isdeleted']=='false' and i['isApproved']=='true' and i['accessType']!='console'):
            count_terminal = count_terminal+1
            expired_perms_terminal[count_terminal]={'id':i['id'],'user':i['user'],'accessType':i['accessType'],'AccessKeyId':i['AccessKeyId'],'account_id':i['account_id'],'policy_arn':i['policy_arn']}
    print("expired_perms_terminal", expired_perms_terminal)
    print("expired_perms_console", expired_perms_console)
    if (len(expired_perms_console) == 0 and len(expired_perms_terminal) != 0):
         detach_user_policy(expired_perms_terminal)
         time.sleep(5)
         delete_accesskeys(expired_perms_terminal)
         time.sleep(5)
         delete_profile(expired_perms_terminal)
         time.sleep(7)
         update_dynamo_db(expired_perms_terminal)
         time.sleep(5)
    if (len(expired_perms_console) != 0 and len(expired_perms_terminal) == 0):
        detach_user_policy(expired_perms_console)
        time.sleep(5)
        disable_login(expired_perms_console)
        time.sleep(5)
        delete_profile(expired_perms_console)
        time.sleep(7)
        update_dynamo_db(expired_perms_console)
        time.sleep(5)
    if(len(expired_perms_console) != 0 and len(expired_perms_terminal) != 0):
        detach_user_policy(expired_perms_terminal)
        time.sleep(5)
        detach_user_policy(expired_perms_console)
        time.sleep(5)
        disable_login(expired_perms_console)
        time.sleep(5)
        delete_accesskeys(expired_perms_terminal)
        time.sleep(5)
        delete_profile(expired_perms_terminal)
        time.sleep(7)
        delete_profile(expired_perms_console)
        time.sleep(7)   
        update_dynamo_db(expired_perms_console)
        time.sleep(5)   
        update_dynamo_db(expired_perms_terminal)   
        time.sleep(5) 
    
def detach_user_policy(expired_perms):
    """
    This method disables the login profile for console users after the timeperiod of access ends.
    """
    try:
        for i in expired_perms:
            user=expired_perms[i]['user']
            id=expired_perms[i]['id']
            account_id=expired_perms[i]['account_id']
            policy_arn=expired_perms[i]['policy_arn']
            
            sts_client = boto3.client('sts')
            cross_account_role_arn = f'arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole'
            credentials = sts_client.assume_role(
            RoleArn=cross_account_role_arn,
            RoleSessionName='TemporaryRoleForElevatedAccess'
            )['Credentials']
            
            
            client = boto3.client('iam',
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'])
            client.detach_user_policy(
                UserName=user,
                PolicyArn=policy_arn
            )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntityException':
            print("Permissions already detached for user:",user)
    
def disable_login(expired_perms):
    """
    This method disables the login profile for console users after the timeperiod of access ends.
    """
    try:
        for i in expired_perms:
            user=expired_perms[i]['user']
            id=expired_perms[i]['id']
            accessType=expired_perms[i]['accessType']
            account_id=expired_perms[i]['account_id']
            
            sts_client = boto3.client('sts')
            cross_account_role_arn = f'arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole'
            credentials = sts_client.assume_role(
            RoleArn=cross_account_role_arn,
            RoleSessionName='TemporaryRoleForElevatedAccess'
            )['Credentials']
            
            client = boto3.client('iam',
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'])
            response = client.delete_login_profile(
            UserName=user
            )
            print("Deleted console login profile for: ",user)
            print("\n")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntityException':
            print("Login Profile for Console Already Deleted for user: ",user)

def delete_accesskeys(expired_perms):
    """
    This method removes the programmatic access for users after the timeperiod of access ends.
    """
    try:
        for i in expired_perms:
            user=expired_perms[i]['user']
            id=expired_perms[i]['id']
            accessType=expired_perms[i]['accessType']
            account_id=expired_perms[i]['account_id']
            
            sts_client = boto3.client('sts')
            cross_account_role_arn = f'arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole'
            credentials = sts_client.assume_role(
            RoleArn=cross_account_role_arn,
            RoleSessionName='TemporaryRoleForElevatedAccess'
            )['Credentials']
            
            if(accessType == 'terminal'):
                accesskeys=expired_perms[i]['AccessKeyId']
                if(accesskeys != 'Access Key Exists'):
                    client = boto3.client('iam',
                        aws_access_key_id=credentials['AccessKeyId'],
                        aws_secret_access_key=credentials['SecretAccessKey'],
                        aws_session_token=credentials['SessionToken'])  
                    response = client.delete_access_key(
                    UserName=user,
                    AccessKeyId=accesskeys
                    )   
                    print("Deleted Programmatic Access Keys for: ",user)
                    print("\n")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntityException':
            print("Login Profile for Console Already Deleted for user: ",user)

def delete_profile(expired_perms):
    """
    This method is used to delete IAM users after the timeperiod of their access ends.
    """
    try:
        for i in expired_perms:
            user=expired_perms[i]['user']
            id=expired_perms[i]['id']
            account_id=expired_perms[i]['account_id']
            
            sts_client = boto3.client('sts')
            cross_account_role_arn = f'arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole'
            credentials = sts_client.assume_role(
            RoleArn=cross_account_role_arn,
            RoleSessionName='TemporaryRoleForElevatedAccess'
            )['Credentials']
            
            client = boto3.client('iam',
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'])  
            response = client.delete_user(
            UserName=user
            )
            print("Deleted IAM Profile for: ",user)
            print("\n")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntityException':
            print("Profile Already Deleted",e.response['Error']['Code'])
    
def update_dynamo_db(expired_perms):
    """
    Simple function just updates the isdeleted column with "true" after successful permission detachment.
    """
    try:
        for i in expired_perms:
            id=expired_perms[i]['id']
            dynamodb=boto3.resource('dynamodb')
            table=dynamodb.Table('elevate-access-request')
            response= table.update_item(
                Key={'id':id},
                UpdateExpression="SET isdeleted=:s",
                ExpressionAttributeValues={':s':"true"},
                ReturnValues="UPDATED_NEW"
            )
            print("Update Dynamo DB isdeleted column as True for id: ",id)
    except Exception as e:
        print(e)

# Beta Version Feature...

# def announce_deletion(expired_perms):
#     """
#     This method is used to announce the deletion that takes places based the scheduler
#     """
#     try:
#         for i in expired_perms:
#             user=expired_perms[i]['user']
#             print("Delete Notification sent for user: ",user)
#             account_id=expired_perms[i]['account_id']
#             client = boto3.client("sns")
#             response = client.publish(
#             TopicArn="ENTER YOUR SNS TOPIC ARN",
#             Subject='IAM Login Profile Deleted for user: ' + user,
#             Message="""
#                 \n \n \n"""

#                 """\n \n \n This email is to inform that AWS Login Profile created by user """ +user+""" has been deleted """

#                 """\n \n \n Account ID: """+account_id+

#                 """\n \n ---------------------------------------------------------------------------------
#                 """,
#             MessageAttributes={
#             'tags': {
#                 'DataType': 'String',
#                 'StringValue' : user
#                 }
#                 })
#     except Exception as e:
#         print(e)