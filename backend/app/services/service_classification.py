from typing import Dict, Optional
import logging
from app.models import UserClassification
from app.database.db_postgresql import PostgreSQL
from app.utils.ai_client import AIClient
from app.caching.cache_redis import RedisCache

logger = logging.getLogger(__name__)

class ClassificationService:
    def __init__(self):
        self.ai_client = AIClient()
        self.cache = RedisCache()
        self.db = PostgreSQL()

    def generate_classification(self, session_id: str) -> Optional[Dict]:
        """Generate final classification based on session data"""
        try:
            # Get session data
            session_data = self.cache.get_session(session_id)
            if not session_data:
                logger.error(f"Session not found: {session_id}")
                return None

            # Generate classification
            classification = self.ai_client.generate_classification(
                content_analysis=session_data['content_analysis'],
                responses=session_data['responses']
            )

            # Save to database
            if not self.db.save_classification(
                session_id,
                classification['interests'],
                classification['relevant_sections']
            ):
                raise Exception("Failed to save classification")

            # Cache results
            self.cache.set_classification(session_id, classification)

            return classification
        except Exception as e:
            logger.error(f"Error generating classification: {e}")
            db.session.rollback()
            return None

    def get_classification(self, session_id: str) -> Optional[Dict]:
        """Get existing classification from cache or database"""
        try:
            # Check cache first
            classification = self.cache.get_classification(session_id)
            if classification:
                return classification

            # Check database
            user_classification = self.db.get_classification(session_id)
            
            if user_classification:
                classification = {
                    'interests': user_classification.interests,
                    'relevant_sections': user_classification.relevant_content
                }
                # Update cache
                self.cache.set_classification(session_id, classification)
                return classification

            return None
        except Exception as e:
            logger.error(f"Error getting classification: {e}")
            return None
