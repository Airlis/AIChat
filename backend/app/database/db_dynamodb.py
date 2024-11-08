import boto3
from flask import current_app

def get_dynamodb_resource():
    return boto3.resource(
        'dynamodb',
        region_name=current_app.config['AWS_REGION'],
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY']
    )

def get_table():
    dynamodb = get_dynamodb_resource()
    table_name = current_app.config['DYNAMODB_SCRAPED_CONTENT_TABLE']
    return dynamodb.Table(table_name)

def get_cached_content(url):
    table = get_table()
    try:
        response = table.get_item(Key={'url': url})
        item = response.get('Item')
        if item:
            return item.get('content'), item.get('last_modified'), item.get('etag')
    except Exception as e:
        print(f"Error fetching from DynamoDB: {e}")
    return None, None, None

def cache_content(url, content, last_modified, etag):
    table = get_table()
    try:
        table.put_item(Item={
            'url': url,
            'content': content,
            'last_modified': last_modified,
            'etag': etag
        })
    except Exception as e:
        print(f"Error saving to DynamoDB: {e}")
