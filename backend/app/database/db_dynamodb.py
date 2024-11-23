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

    def save_content_analysis(self, url: str, content: Dict, analysis: Dict, content_hash: str) -> bool:
        """Save content analysis with content hash"""
        try:
            timestamp = int(datetime.now().timestamp())

            # Serialize analysis
            analysis_json = json.dumps(analysis)

            # Prepare item to store in DynamoDB
            item = {
                'url': url,
                'analysis': analysis_json,
                'content_hash': content_hash,
                'timestamp': timestamp,
                'ttl': timestamp + (self.content_ttl_days * 24 * 3600)
            }

            # Optionally include content if it's small enough
            content_json = json.dumps(content)
            item_size_estimate = len(json.dumps(item)) + len(content_json)
            if item_size_estimate <= 400000:  # DynamoDB item size limit is 400KB
                item['content'] = content_json
            else:
                logger.warning(f"Content too large to store in DynamoDB for URL {url}")

            # Final item size check
            item_size = len(json.dumps(item))
            if item_size > 400000:
                logger.error(f"Final item size ({item_size} bytes) exceeds DynamoDB limit")
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
