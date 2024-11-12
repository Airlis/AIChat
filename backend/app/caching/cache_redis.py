from typing import Dict, Optional
import json
from redis import Redis
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        self.redis = Redis.from_url(
            current_app.config['CACHE_REDIS_URL'],
            decode_responses=True
        )
        self.content_timeout = 86400  # 1 day in seconds
        self.session_timeout = 3600   # 1 hour in seconds

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        key = f"session:{session_id}"
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis get error for session {session_id}: {e}")
            return None

    def set_session(self, session_id: str, session_data: Dict) -> bool:
        """Cache session data"""
        key = f"session:{session_id}"
        try:
            success = self.redis.setex(
                key,
                self.session_timeout,
                json.dumps(session_data)
            )
            return bool(success)
        except Exception as e:
            logger.error(f"Redis set error for session {session_id}: {e}")
            return False

    def get_content_analysis(self, content_hash: str) -> Optional[Dict]:
        """Get cached content analysis using content hash"""
        key = f"content:{content_hash}"
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis get error for content hash {content_hash}: {e}")
            return None

    def set_content_analysis(self, content_hash: str, analysis: Dict) -> bool:
        """Cache content analysis using content hash"""
        key = f"content:{content_hash}"
        try:
            success = self.redis.setex(
                key,
                self.content_timeout,
                json.dumps(analysis)
            )
            return bool(success)
        except Exception as e:
            logger.error(f"Redis set error for content hash {content_hash}: {e}")
            return False

    def get_classification(self, session_id: str) -> Optional[Dict]:
        """Get cached classification"""
        key = f"classification:{session_id}"
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis get error for classification {session_id}: {e}")
            return None

    def set_classification(self, session_id: str, classification: Dict) -> bool:
        """Cache classification"""
        key = f"classification:{session_id}"
        try:
            success = self.redis.setex(
                key,
                self.content_timeout,
                json.dumps(classification)
            )
            return bool(success)
        except Exception as e:
            logger.error(f"Redis set error for classification {session_id}: {e}")
            return False

    def get_first_question(self, content_hash: str) -> Optional[Dict]:
        """Get cached first question and options based on content hash"""
        key = f"first_question:{content_hash}"
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis get error for first question {content_hash}: {e}")
            return None

    def set_first_question(self, content_hash: str, question_data: Dict) -> bool:
        """Cache first question and options based on content hash"""
        key = f"first_question:{content_hash}"
        try:
            success = self.redis.setex(
                key,
                self.content_timeout,
                json.dumps(question_data)
            )
            return bool(success)
        except Exception as e:
            logger.error(f"Redis set error for first question {content_hash}: {e}")
            return False
