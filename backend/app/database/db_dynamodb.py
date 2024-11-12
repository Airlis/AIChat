import boto3
import json
from typing import Dict, Optional
import logging
from datetime import datetime
from flask import current_app
from hashlib import sha256
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class DynamoDB:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=current_app.config['AWS_REGION']
        )
        self.content_table = self.dynamodb.Table(current_app.config['DYNAMODB_SCRAPED_CONTENT_TABLE'])
        self.content_ttl_days = int(current_app.config.get('CONTENT_TTL_DAYS', 7))

    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content"""
        return sha256(content.encode('utf-8')).hexdigest()

    def save_content_analysis(self, url: str, content: Dict, analysis: Dict) -> bool:
        """Save content analysis with content hash"""
        try:
            timestamp = int(datetime.now().timestamp())
            content_hash = self._calculate_content_hash(json.dumps(content))

            item = {
                'url': url,
                'content': json.dumps(content),
                'analysis': json.dumps(analysis),
                'content_hash': content_hash,
                'timestamp': timestamp,
                'ttl': timestamp + (self.content_ttl_days * 24 * 3600)
            }

            # Check item size to avoid DynamoDB limits
            item_size = len(json.dumps(item))
            if item_size > 400000:  # DynamoDB item size limit is 400KB
                logger.error(f"Item size ({item_size} bytes) exceeds DynamoDB limit")
                return False

            logger.info(f"Saving to DynamoDB - URL: {url}, Hash: {content_hash}")
            self.content_table.put_item(Item=item)
            return True
        except ClientError as e:
            logger.exception(f"DynamoDB ClientError for URL {url}: {e}")
            return False
        except Exception as e:
            logger.error(f"DynamoDB save error for URL {url}: {e}")
            logger.exception("Full traceback:")
            return False

    def get_content_analysis(self, url: str) -> Optional[Dict]:
        """Get content analysis from DynamoDB"""
        try:
            logger.info(f"Fetching content from DynamoDB for URL: {url}")
            response = self.content_table.get_item(
                Key={'url': url}
            )

            item = response.get('Item')
            if not item:
                logger.info(f"No item found in DynamoDB for URL: {url}")
                return None

            content = json.loads(item['content'])
            analysis = json.loads(item['analysis'])
            timestamp = int(float(item['timestamp']))
            content_hash = item['content_hash']

            return {
                'content': content,
                'analysis': analysis,
                'content_hash': content_hash,
                'timestamp': timestamp
            }
        except Exception as e:
            logger.error(f"DynamoDB get error for URL {url}: {str(e)}")
            logger.exception("Full traceback:")
            return None
