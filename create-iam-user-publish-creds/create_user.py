import boto3
import botocore
from botocore.exceptions import ClientError

class CreateUser:
    def __init__(
        self, id, username, password, permissionsboundary, path, account_id
    ) -> None:
        self.id = id
        self.username = username
        self.password = password
        self.permissionsboundary = permissionsboundary
        self.path = path
        self.account_id = account_id

    def create_iam_user(self):
        """
        Method to create an IAM user and assign permissions to him/her
        """
        try:
            sts_client = boto3.client('sts')
            cross_account_role_arn = f'arn:aws:iam::{self.account_id}:role/OrganizationAccountAccessRole'
            credentials = sts_client.assume_role(
            RoleArn=cross_account_role_arn,
            RoleSessionName='TemporaryRoleForElevatedAccess'
            )['Credentials']

            client = boto3.resource("iam",
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
            
            response = client.create_user(
                Path=self.path,
                UserName=self.username,
                Tags=[
                    {"Key": "app", "Value": "privilege-access-portal"},
                ],
            )
            print(response)
            return response
        except client.meta.client.exceptions.EntityAlreadyExistsException as e:
            print("User already exists")
            return e.response['Error']['Code'] 

    def create_console_access(self):
        """
        Creates AWS Console Access
        """
        login_details = {}
        try:
            sts_client = boto3.client('sts')
            cross_account_role_arn = f'arn:aws:iam::{self.account_id}:role/OrganizationAccountAccessRole'
            credentials = sts_client.assume_role(
            RoleArn=cross_account_role_arn,
            RoleSessionName='TemporaryRoleForElevatedAccess'
            )['Credentials']
            
            client = boto3.resource("iam",           
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
            
            user = client.User(self.username)
            login_profile = user.create_login_profile(
                Password=self.password, PasswordResetRequired=True
            )
            print(
                login_profile,
                " ",
                "\nUsername:",
                self.username,
                " ",
                "\nPassword:",
                self.password,
                "\nSign-In Link: "
                f"https://{self.account_id}.signin.aws.amazon.com/console",
            )
            login_details["Username"] = self.username
            login_details["Password"] = self.password
            login_link = f"https://{self.account_id}.signin.aws.amazon.com/console"
            login_details["Link"] = login_link
            return login_details
        except client.meta.client.exceptions.EntityAlreadyExistsException as e:
            print("Login Profile already exists")
            return e.response['Error']['Code']
        
    def create_programmatic_access(self):
        """
        Creates AWS Programmatic Access - generates Access Key and Secret Key
        """
        credentials = {}
        try:
            sts_client = boto3.client('sts')
            cross_account_role_arn = f'arn:aws:iam::{self.account_id}:role/OrganizationAccountAccessRole'
            credentials = sts_client.assume_role(
            RoleArn=cross_account_role_arn,
            RoleSessionName='TemporaryRoleForElevatedAccess'
            )['Credentials']
        
            iam = boto3.client("iam",
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
            
            access_secrete_key = iam.create_access_key(UserName=self.username)
            access_key = access_secrete_key["AccessKey"]["AccessKeyId"]
            secret_key = access_secrete_key["AccessKey"]["SecretAccessKey"]
            print("Access Key: ", access_key, "\nSecret Key: ", secret_key)
            credentials["AccessKeyId"] = access_key
            credentials["SecretAccessKey"] = secret_key
            return credentials
        except ClientError as e:
            print("Error Defination:",e.response['Error']['Code'])
            if e.response['Error']['Code'] == 'LimitExceeded':
                return e.response['Error']['Code']
            
    def attach_user_policy(self):
        try:
            sts_client = boto3.client('sts')
            cross_account_role_arn = f'arn:aws:iam::{self.account_id}:role/OrganizationAccountAccessRole'
            credentials = sts_client.assume_role(
            RoleArn=cross_account_role_arn,
            RoleSessionName='TemporaryRoleForElevatedAccess'
            )['Credentials']
        
            iam = boto3.client("iam",
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
            
            response = iam.attach_user_policy(
            UserName=self.username,
            PolicyArn=self.permissionsboundary
            )
            print("User Existed - So attaching the policy")
        except Exception as e:
            print(e)