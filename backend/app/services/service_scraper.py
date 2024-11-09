from typing import Dict, Optional
import logging
from datetime import datetime, timedelta
from app.utils.scraper import WebScraper
from app.utils.ai_client import AIClient
from app.database.db_dynamodb import DynamoDB
from app.caching.cache_redis import RedisCache

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
            content_data = self.scraper.scrape_content(url)
            if not content_data or not content_data.get('sections'):
                raise ValueError("No content scraped from URL")

            # Extract text for analysis
            text_content = "\n\n".join(
                section['text'] for section in content_data['sections']
                if section.get('text')
            )

            if not text_content:
                raise ValueError("No text content extracted from URL")

            # Analyze content
            content_analysis = self.ai_client.analyze_content(text_content)
            if not content_analysis:
                raise ValueError("Content analysis failed")

            result = {
                'content': content_data,
                'analysis': content_analysis
            }

            # Try to cache the result
            try:
                self.redis_cache.set_content_analysis(url, result)
                self.dynamodb.save_content_analysis(
                    url=url,
                    content=content_data,
                    analysis=content_analysis
                )
            except Exception as e:
                logger.warning(f"Cache storage error for {url}: {e}")
                # Continue even if caching fails

            return result

        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            return None