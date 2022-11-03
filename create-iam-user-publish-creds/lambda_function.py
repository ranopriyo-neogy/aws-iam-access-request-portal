from datetime import datetime
import secrets
from create_user import CreateUser
import boto3
import json
from boto3.dynamodb.conditions import Key
def lambda_handler(event, context):
    print("received event:")
    try:
        if (
            event["Records"][0]["eventName"] == "INSERT"
            or event["Records"][0]["eventName"] == "MODIFY"
            or event["Records"][0]["eventName"] == "REMOVE"
        ):
            print("The recorded event is:", event["Records"][0]["eventName"])
            check_database_insert_event(event["Records"][0])
            newImage = event["Records"][0]["dynamodb"]["NewImage"]
            id = newImage["id"]["S"]
            executionCount = newImage["executionCount"]["S"]
            if(executionCount == "1"):
                publish_event(id)
                publish_changes(event['Records'][0])
    except Exception as e:
        print(e)


def check_database_insert_event(record):
    """
    This function checks database insert events and create the user upon specific conditions
    """
    credentials = {}
    try:
        terminal_creds = ""
        newImage = record["dynamodb"]["NewImage"]
        id = newImage["id"]["S"]
        account_id = newImage["account_id"]["S"]
        user = newImage["user"]["S"]
        todate = newImage["todate"]["S"]
        policy_arn = newImage["policy_arn"]["S"]
        isdeleted = newImage["isdeleted"]["S"]
        isApproved = newImage["isApproved"]["S"]
        accessType = newImage["accessType"]["S"]
        password = newImage["password"]["S"]
        executionCount = newImage["executionCount"]["S"]
        print(
            "executionCount:",
            executionCount,
            " isdeleted:",
            isdeleted,
            " isApproved:",
            isApproved,
        )
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if (
            isdeleted == "false"
            and isApproved == "true"
            and todate > current_time
            and executionCount == "1"
        ):
            createuserobject = CreateUser(
                id, user, password, policy_arn, "/", account_id
            )
            message = createuserobject.create_iam_user()
            createuserobject.attach_user_policy()
            if accessType == "console":
                credentials = createuserobject.create_console_access()
                # createuserobject.attach_user_policy()
                insert_to_db(id, credentials,account_id,policy_arn,user)
            if accessType == "terminal":
                terminal_creds = createuserobject.create_programmatic_access()
                # createuserobject.attach_user_policy()
                print("Terminal Creds: ",terminal_creds)
                insert_to_db(id, terminal_creds,account_id,policy_arn,user)
                    
    except Exception as e:
        print(e)


def insert_to_db(id, credentials,account_id,policy,user):
    """
    This function updates the dynamoDB with the credentials
    """
    try:
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table("elevate-access-request")
        print("Crendetials:", credentials)
        if(credentials != "EntityAlreadyExists"):
            if(credentials != "LimitExceeded"):
                for key, value in credentials.items():
                    if key == "password" and value != "NA":
                        table.update_item(
                            Key={"id": id},
                            UpdateExpression="SET Password = :val , executionCount = :count",
                            ExpressionAttributeValues={
                                ":val": value,
                                ":count": "2",
                            },
                        )
                    if key == "Link":
                        table.update_item(
                            Key={"id": id},
                            UpdateExpression="SET Link = :val , executionCount = :count",
                            ExpressionAttributeValues={
                                ":val": value,
                                ":count": "2",
                            },
                        )
                    if key == "AccessKeyId":
                        table.update_item(
                            Key={"id": id},
                            UpdateExpression="SET AccessKeyId = :val , executionCount = :count",
                            ExpressionAttributeValues={
                                ":val": value,
                                ":count": "2",
                            },
                        )
                    if key == "SecretAccessKey":
                        table.update_item(
                            Key={"id": id},
                            UpdateExpression="SET SecretAccessKey = :val , executionCount = :count",
                            ExpressionAttributeValues={
                                ":val": value,
                                ":count": "2",
                            },
                        )
            else:
                table.update_item(
                    Key={"id": id},
                    UpdateExpression="SET password = :val1 , executionCount = :count , AccessKeyId = :val2 , SecretAccessKey = :val3",
                    ExpressionAttributeValues={
                        ":val1": 'Password Exists',
                        ":val2": 'Access Key Exists',
                        ":val3": 'Secret Access Key Exists',
                        ":count": "2",
                    },
                )   
                policy_attached_notification(id,account_id,policy,user)
        else:
            table.update_item(
                Key={"id": id},
                UpdateExpression="SET password = :val1 , executionCount = :count , AccessKeyId = :val2 , SecretAccessKey = :val3",
                ExpressionAttributeValues={
                    ":val1": 'Password Exists',
                    ":val2": 'Access Key Exists',
                    ":val3": 'Secret Access Key Exists',
                    ":count": "2",
                },
            )
            policy_attached_notification(id,account_id,policy,user)
            
    except Exception as e:
        print(e)

def publish_event(id):
    """
    Method to fetch record from DB and Publish to SNS
    """
    try:
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table("elevate-access-request")
        data = table.query(KeyConditionExpression=Key('id').eq(id)) 
        client = boto3.client("sns")
        for i in data['Items']:
            username = i['user']
            password = i['password']
            account_id = i['account_id']
            isApproved = i['isApproved']
            if(password == 'NA' and isApproved == 'true'):
                accesskey = i['AccessKeyId']
                secretsaccesskey = i['SecretAccessKey']
                client.publish(
                TopicArn="ENTER YOUR SNS TOPIC ARN",
                Subject='AWS Login Credentials for: ' + username,
                Message="""
                    \n \n \n AWS Account ID: """ +account_id+
        
                    """\n \n \n User: """ +username+
        
                    """\n \n \n Access Key: """ +accesskey+

                    """\n \n \n Secret Access Key: """ +secretsaccesskey+
            
                    """\n \n ---------------------------------------------------------------------------------
                    """,
                MessageAttributes={
                    'tags': {
                            'DataType': 'String',
                            'StringValue' : id
                            }
                }
                )
            if(password != 'NA' and isApproved == 'true' and password != 'Password Exists'):
                loginlink = i['Link']
                client.publish(
                TopicArn="ENTER YOUR SNS TOPIC ARN",
                Subject='AWS Login Credentials for: ' + username,
                Message="""
                    \n \n \n AWS Account ID: """ +account_id+
        
                    """\n \n \n Username: """ +username+
        
                    """\n \n \n Password: """ +password+

                    """\n \n \n Login Link: """ +loginlink+
            
                    """\n \n ---------------------------------------------------------------------------------
                    """,
                MessageAttributes={
                    'tags': {
                            'DataType': 'String',
                            'StringValue' : id
                            }
                }
                )
        return{
            'statusCode':200
        }
    except Exception as e:
        print(e)
    
def publish_changes(record):
    try:
        newImage = record['dynamodb']['NewImage']
        id = newImage['id']['S']
        account_id = newImage['account_id']['S']
        user = newImage['user']['S']
        fromdate = newImage['fromdate']['S']
        todate = newImage['todate']['S']
        policy = newImage['policy_arn']['S']
        accessType = newImage['accessType']['S']
        reason = newImage['reason']['S']
        isdeleted = newImage['isdeleted']['S']
        isApproved = newImage['isApproved']['S']
        client = boto3.client("sns")
        response = client.publish(
        TopicArn="ENTER YOUR SNS TOPIC ARN",
        Subject='Access Elevation Request Portal - New Request: ' + user,
        Message="""
            \n \n \n Id: """ +id+

            """\n \n \n AWS Account: """ +account_id+

            """\n \n \n User: """ +user+

            """\n \n \n From Date (UTC): """ +fromdate+

            """\n \n \n To Date (UTC): """ +todate+

            """\n \n \n Policy: """ +policy+

             """\n \n \n Access Type: """ +accessType+

            """\n \n \n Reason: """ +reason+

            """\n \n \n Deleted: """ +isdeleted+

            """\n \n \n isApproved: """ +isApproved+

            """\n \n ---------------------------------------------------------------------------------
            """,
        MessageAttributes={
            'tags': {
                'DataType': 'String',
                'StringValue' : user
            }
        }
        )
        return{
            'statusCode':200,
            'body':json.dumps(response)
        }
    except Exception as e:
        print(e)
        
def policy_attached_notification(id,account_id,policy,user):
    try:
        client = boto3.client("sns")
        response = client.publish(
        TopicArn="ENTER YOUR SNS TOPIC ARN",
        Subject='Access Elevation Request Portal - Policy Attached To: ' + user,
        Message="""
            \n \n \n Id: """ +id+

            """\n \n \n AWS Account: """ +account_id+

            """\n \n \n User: """ +user+

            """\n \n \n Policy: """ +policy+

            """\n \n ---------------------------------------------------------------------------------
            """,
        MessageAttributes={
            'tags': {
                'DataType': 'String',
                'StringValue' : user
            }
        }
        )
        return{
            'statusCode':200,
            'body':json.dumps(response)
        }
    except Exception as e:
        print(e)
        
