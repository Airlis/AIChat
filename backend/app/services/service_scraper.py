from typing import Dict, Optional
import logging
from datetime import datetime, timedelta
from app.utils.scraper import WebScraper
from app.utils.ai_client import AIClient
from app.database.db_dynamodb import DynamoDB
from app.caching.cache_redis import RedisCache
import json
import hashlib

logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self):
        self.scraper = WebScraper()
        self.ai_client = AIClient()
        self.dynamodb = DynamoDB()
        self.redis_cache = RedisCache()
        self.content_update_threshold = timedelta(days=2)  # Content refresh after 2 days

    def _calculate_content_hash(self, content: Dict) -> str:
        """Calculate SHA-256 hash of content"""
        # Clean content to remove dynamic elements
        cleaned_content = self._clean_content_for_hashing(content)
        return hashlib.sha256(json.dumps(cleaned_content, sort_keys=True).encode('utf-8')).hexdigest()

    def _clean_content_for_hashing(self, content: Dict) -> Dict:
        """Remove or normalize dynamic elements from content"""
        # Example: Remove timestamps, session IDs, dynamic ads, etc.
        cleaned_sections = []
        for section in content.get('sections', []):
            cleaned_section = {
                'text': section.get('text', ''),
                # Exclude or normalize other fields as needed
            }
            cleaned_sections.append(cleaned_section)
        return {
            'url': content.get('url', ''),
            'title': content.get('title', ''),
            'sections': cleaned_sections
        }

    def process_url(self, url: str) -> Optional[Dict]:
        """Process URL: scrape, analyze, and cache content"""
        try:
            # Normalize URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Scrape current content
            content = self.scraper.scrape_content(url)
            if not content:
                raise ValueError(f"Failed to scrape content from {url}")

            # Calculate content hash
            current_content_hash = self._calculate_content_hash(content)

            # Check Redis cache using content hash
            cached_content = self.redis_cache.get_content_analysis(current_content_hash)
            if cached_content:
                logger.info(f"Using cached content from Redis for {url}")
                result = cached_content
            else:
                # Check DynamoDB
                dynamo_content = self.dynamodb.get_content_analysis(url)
                if dynamo_content and dynamo_content['content_hash'] == current_content_hash:
                    logger.info(f"Using cached content from DynamoDB for {url}")
                    result = {
                        'content': dynamo_content['content'],
                        'analysis': dynamo_content['analysis']
                    }
                    # Cache in Redis
                    self.redis_cache.set_content_analysis(current_content_hash, result)
                else:
                    logger.info(f"Content has changed or not found. Analyzing new content for {url}")
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

                    # Cache the result
                    self.redis_cache.set_content_analysis(current_content_hash, result)

                    # Save to DynamoDB
                    self.dynamodb.save_content_analysis(
                        url=url,
                        content=content,
                        analysis=content_analysis
                    )

            # Check for cached first question
            first_question = self.redis_cache.get_first_question(current_content_hash)
            if first_question:
                logger.info(f"Using cached first question for content hash {current_content_hash}")
                result['first_question'] = first_question
            else:
                logger.info(f"Generating new first question for content hash {current_content_hash}")
                # Generate first question
                question = self.ai_client.generate_first_question(
                    content_analysis=result['analysis']
                )
                result['first_question'] = question
                # Cache the first question
                self.redis_cache.set_first_question(current_content_hash, question)

            # Return result along with first question
            return {
                'content': result['content'],
                'analysis': result['analysis'],
                'first_question': result['first_question'],
                'content_hash': current_content_hash
            }

        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            return None
