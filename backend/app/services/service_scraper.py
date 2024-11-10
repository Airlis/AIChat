from typing import Dict, Optional
import logging
from datetime import datetime, timedelta
from app.utils.scraper import WebScraper
from app.utils.ai_client import AIClient
from app.database.db_dynamodb import DynamoDB
from app.caching.cache_redis import RedisCache
import json

logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self):
        self.scraper = WebScraper()
        self.ai_client = AIClient()
        self.dynamodb = DynamoDB()
        self.redis_cache = RedisCache()
        self.content_update_threshold = timedelta(days=2)  # Content refresh after 2 days

    def process_url(self, url: str) -> Optional[Dict]:
        """Process URL: scrape, analyze, and cache content"""
        try:
            # Normalize URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            try:
                # Check Redis cache first
                cached_content = self.redis_cache.get_content_analysis(url)
                if cached_content:
                    logger.info(f"Using cached content for {url}")
                    return cached_content

                # Check DynamoDB
                dynamo_content = self.dynamodb.get_content_analysis(url)
                if dynamo_content:
                    logger.info(f"Using DynamoDB content for {url}")
                    self.redis_cache.set_content_analysis(url, dynamo_content)
                    return dynamo_content
            except Exception as e:
                logger.warning(f"Cache retrieval error for {url}: {e}")
                # Continue with scraping if cache fails

            # Scrape and analyze new content
            content = self.scraper.scrape_content(url)
            if not content:
                raise ValueError(f"Failed to scrape content from {url}")

            # Extract text for analysis
            text_content = "\n\n".join(
                section['text'] for section in content['sections']
                if section.get('text')
            )

            if not text_content:
                raise ValueError("No text content extracted from URL")

            # Analyze content
            content_analysis = self.ai_client.analyze_content(text_content)
            if not content_analysis:
                raise ValueError("Content analysis failed")

            result = {
                'content': content,
                'analysis': content_analysis
            }

            # Try to cache the result
            try:
                # Cache in Redis
                if not self.redis_cache.set_content_analysis(url, result):
                    logger.error(f"Redis cache save failed for URL {url}")
                
                # Save to DynamoDB with size check
                content_size = len(json.dumps(content))
                analysis_size = len(json.dumps(content_analysis))
                logger.info(f"Content size: {content_size}, Analysis size: {analysis_size}")
                
                if content_size + analysis_size > 380000:  # Leave buffer for other fields
                    logger.warning("Content too large for DynamoDB, truncating...")
                    # Truncate content to fit
                    while content_size + analysis_size > 380000:
                        if len(content['sections']) > 1:
                            content['sections'].pop()
                            content_size = len(json.dumps(content))
                
                dynamo_success = self.dynamodb.save_content_analysis(
                    url=url,
                    content=content,
                    analysis=content_analysis
                )
                if not dynamo_success:
                    logger.error(f"DynamoDB save failed for URL {url}")
                    
            except Exception as e:
                logger.error(f"Storage error for {url}: {str(e)}")
                logger.exception("Full traceback:")
                # Continue even if storage fails

            return result

        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            return None