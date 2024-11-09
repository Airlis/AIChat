import boto3
import json
from typing import Dict, Optional, Tuple
import logging
from datetime import datetime
from flask import current_app
from hashlib import sha256

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
        self.content_ttl_days = current_app.config.get('CONTENT_TTL_DAYS', 7)

    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content"""
        return sha256(content.encode('utf-8')).hexdigest()

    def save_content_analysis(self, url: str, content: Dict, analysis: Dict) -> bool:
        """Save content analysis with content hash"""
        try:
            timestamp = int(datetime.now().timestamp())
            content_hash = self._calculate_content_hash(str(content))
            
            # Ensure analysis has required structure
            if not isinstance(analysis, dict):
                analysis = {
                    "topics": ["General Content"],
                    "audience": ["Website Visitors"],
                    "sections": ["Main Content"]
                }
            
            item = {
                'url': url,
                'content': json.dumps(content),
                'analysis': json.dumps(analysis),
                'content_hash': content_hash,
                'timestamp': timestamp,
                'ttl': timestamp + (self.content_ttl_days * 24 * 3600)
            }
            
            # Validate all required fields are present
            required_fields = ['url', 'content', 'analysis', 'content_hash', 'timestamp', 'ttl']
            missing_fields = [field for field in required_fields if field not in item]
            if missing_fields:
                logger.error(f"Missing required fields in item: {missing_fields}")
                return False
            
            logger.info(f"Saving to DynamoDB - URL: {url}, Hash: {content_hash}")
            self.content_table.put_item(Item=item)
            return True
        except Exception as e:
            logger.error(f"DynamoDB save error for URL {url}: {e}")
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

            logger.info(f"DynamoDB item fields: {list(item.keys())}")

            # Ensure all required fields exist
            required_fields = ['content', 'analysis', 'timestamp', 'content_hash']
            missing_fields = [field for field in required_fields if field not in item]
            if missing_fields:
                logger.error(f"Missing fields in DynamoDB item: {missing_fields}")
                return None

            logger.info(f"Field types - timestamp: {type(item['timestamp'])}, "
                       f"content: {type(item['content'])}, "
                       f"analysis: {type(item['analysis'])}")

            try:
                timestamp = int(float(item['timestamp']))
                ttl = int(float(item['ttl'])) if 'ttl' in item else None
                logger.info(f"Converted timestamp: {timestamp}, TTL: {ttl}")
            except (TypeError, ValueError) as e:
                logger.error(f"Timestamp conversion error: {str(e)}")
                logger.error(f"Raw timestamp value: {item['timestamp']}")
                return None

            try:
                content = json.loads(item['content'])
                analysis = json.loads(item['analysis'])
                logger.info("Successfully parsed content and analysis JSON")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                logger.error(f"Raw content: {item['content'][:100]}...")
                logger.error(f"Raw analysis: {item['analysis'][:100]}...")
                return None

            return {
                'content': content,
                'analysis': analysis,
                'content_hash': item['content_hash'],
                'timestamp': timestamp
            }
        except Exception as e:
            logger.error(f"DynamoDB get error for URL {url}: {str(e)}")
            logger.exception("Full traceback:")  # This will log the full stack trace
            return None

    def update_timestamp(self, url: str) -> bool:
        """Update timestamp and TTL for existing content"""
        try:
            timestamp = int(datetime.now().timestamp())
            self.content_table.update_item(
                Key={'url': url},
                UpdateExpression='SET #ts = :ts, #ttl = :ttl',
                ExpressionAttributeNames={
                    '#ts': 'timestamp',
                    '#ttl': 'ttl'
                },
                ExpressionAttributeValues={
                    ':ts': timestamp,
                    ':ttl': timestamp + (self.content_ttl_days * 24 * 3600)
                }
            )
            return True
        except Exception as e:
            logger.error(f"DynamoDB update error for URL {url}: {e}")
            return False
