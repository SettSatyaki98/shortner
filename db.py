import os
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from logger import get_logger
from config import AWS_REGION

logger = get_logger(__name__)

# 1. Config and Resource Instantiation
dynamodb_kwargs = {'region_name': AWS_REGION}
if os.getenv("DYNAMODB_ENDPOINT_URL"):
    dynamodb_kwargs['endpoint_url'] = os.getenv("DYNAMODB_ENDPOINT_URL")

dynamodb = boto3.resource('dynamodb', **dynamodb_kwargs)

users_table = dynamodb.Table('bitly-users')
urls_table = dynamodb.Table('bitly-urls')

# 2. Table Setup
def setup_dynamodb_tables():
    try:
        dynamodb.create_table(
            TableName='bitly-users',
            KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceInUseException':
            logger.error(f"Error creating bitly-users: {e}")

    try:
        dynamodb.create_table(
            TableName='bitly-urls',
            KeySchema=[{'AttributeName': 'short_code', 'KeyType': 'HASH'}],
            AttributeDefinitions=[
                {'AttributeName': 'short_code', 'AttributeType': 'S'},
                {'AttributeName': 'userid', 'AttributeType': 'S'},
                {'AttributeName': 'sysdate', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'UserIdIndex',
                    'KeySchema': [
                        {'AttributeName': 'userid', 'KeyType': 'HASH'},
                        {'AttributeName': 'sysdate', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceInUseException':
            logger.error(f"Error creating bitly-urls: {e}")

# 3. Data Access Wrappers

def get_user_by_email(email: str):
    try:
        response = users_table.get_item(Key={'email': email})
        return response.get('Item')
    except ClientError:
        return None

def create_user(email: str, name: str, password_hash: str):
    users_table.put_item(Item={
        'email': email,
        'name': name,
        'password': password_hash
    })

def fetch_user_urls_desc(email: str):
    try:
        response = urls_table.query(
            IndexName='UserIdIndex',
            KeyConditionExpression=Key('userid').eq(email),
            ScanIndexForward=False  # Sort descending by sysdate
        )
        return response.get('Items', [])
    except ClientError as e:
        logger.error(f"Error fetching URLs for {email}: {e}")
        return []

def create_url(short_code: str, long_url: str, email: str, sysdate: str):
    urls_table.put_item(Item={
        'short_code': short_code,
        'long_url': long_url,
        'userid': email,
        'sysdate': sysdate
    })

def get_url_by_short_code(short_code: str):
    try:
        response = urls_table.get_item(Key={'short_code': short_code})
        return response.get('Item')
    except ClientError:
        return None
