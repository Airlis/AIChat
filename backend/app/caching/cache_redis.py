from typing import Dict, Optional
import json
from redis import Redis
from flask import current_app
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        self.redis = Redis.from_url(
            current_app.config['CACHE_REDIS_URL'],
            decode_responses=True
        )
        self.content_timeout = 86400
        self.session_timeout = 3600
        self.max_cache_size = 1000

    def _increment_frequency(self, key: str):
        """Increment access frequency counter for a key"""
        freq_key = f"freq:{key}"
        pipe = self.redis.pipeline()
        pipe.incr(freq_key)
        pipe.expire(freq_key, max(self.content_timeout, self.session_timeout))
        pipe.execute()

    def _get_frequency(self, key: str) -> int:
        """Get access frequency for a key"""
        freq_key = f"freq:{key}"
        freq = self.redis.get(freq_key)
        return int(freq) if freq else 0

    def _evict_if_needed(self):
        """Evict least frequently used items if cache is full"""
        try:
            # Get all keys (excluding frequency counters)
            all_keys = [k for k in self.redis.keys() if not k.startswith('freq:')]
            
            if len(all_keys) >= self.max_cache_size:
                # Get frequencies for all keys
                key_frequencies = [
                    (key, self._get_frequency(key))
                    for key in all_keys
                ]
                
                # Sort by frequency (ascending) and timestamp (oldest first)
                key_frequencies.sort(key=lambda x: x[1])
                
                # Remove least frequently used items
                items_to_remove = len(all_keys) - self.max_cache_size + 1
                for key, _ in key_frequencies[:items_to_remove]:
                    self.redis.delete(key)
                    self.redis.delete(f"freq:{key}")
                
                logger.info(f"Evicted {items_to_remove} least frequently used items from cache")
        except Exception as e:
            logger.error(f"Cache eviction error: {e}")

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data with LFU tracking"""
        key = f"session:{session_id}"
        try:
            data = self.redis.get(key)
            if data:
                self._increment_frequency(key)
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis get error for session {session_id}: {e}")
            return None

    def set_session(self, session_id: str, session_data: Dict) -> bool:
        """Cache session data with LFU management"""
        key = f"session:{session_id}"
        try:
            self._evict_if_needed()
            success = self.redis.setex(
                key,
                self.session_timeout,
                json.dumps(session_data)
            )
            if success:
                self._increment_frequency(key)
            return bool(success)
        except Exception as e:
            logger.error(f"Redis set error for session {session_id}: {e}")
            return False

    def get_content_analysis(self, url: str) -> Optional[Dict]:
        """Get cached content analysis with LFU tracking"""
        key = f"content:{url}"
        try:
            data = self.redis.get(key)
            if data:
                self._increment_frequency(key)
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis get error for content {url}: {e}")
            return None

    def set_content_analysis(self, url: str, analysis: Dict) -> bool:
        """Cache content analysis"""
        key = f"content:{url}"
        try:
            success = self.redis.setex(
                key,
                self.content_timeout,
                json.dumps(analysis)
            )
            if success:
                self._increment_frequency(key)
            return bool(success)
        except Exception as e:
            logger.error(f"Redis set error for content {url}: {e}")
            return False

    def get_classification(self, session_id: str) -> Optional[Dict]:
        """Get cached classification"""
        key = f"classification:{session_id}"
        try:
            data = self.redis.get(key)
            if data:
                self._increment_frequency(key)
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
            if success:
                self._increment_frequency(key)
            return bool(success)
        except Exception as e:
            logger.error(f"Redis set error for classification {session_id}: {e}")
            return False
