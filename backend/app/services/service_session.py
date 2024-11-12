from uuid import uuid4
from typing import Dict, Optional, List
import logging
from datetime import datetime
from app.models import UserSession, UserResponse
from app.extensions import db
from app.caching.cache_redis import RedisCache
from app.utils.ai_client import AIClient
from app.database.db_postgresql import PostgreSQL

logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self):
        self.cache = RedisCache()
        self.ai_client = AIClient()
        self.db = PostgreSQL()
        self.min_questions = 3  # Minimum number of questions before classification
        self.max_questions = 5  # Maximum number of questions before classification

    def create_session(self, url: str, content_analysis: Dict, content_hash: str) -> str:
        """Create new session and generate first question"""
        try:
            session_id = str(uuid4())

            # Save to database
            if not self.db.save_session(session_id, url, content_analysis):
                raise Exception("Failed to save session")

            # Get the cached first question
            first_question = content_analysis.get('first_question')
            if not first_question:
                # Fallback in case first_question is not present
                first_question = self.ai_client.generate_first_question(
                    content_analysis=content_analysis
                )
                # Cache the first question
                self.cache.set_first_question(content_hash, first_question)

            # Cache session data
            session_data = {
                'url': url,
                'content_analysis': content_analysis,
                'current_question': first_question,
                'responses': [],
                'content_hash': content_hash
            }
            self.cache.set_session(session_id, session_data)

            return session_id
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise

    def process_response(self, session_id: str, answer: str) -> Optional[Dict]:
        """Process user response and get next question or classification"""
        try:
            session_data = self.cache.get_session(session_id)
            if not session_data:
                raise ValueError("Session not found")

            # Save current response to database
            current_question = session_data['current_question']
            self.db.save_response(
                session_id=session_id,
                question=current_question['question'],
                answer=answer
            )

            # Save current response
            session_data['responses'].append({
                'question': current_question['question'],
                'answer': answer
            })

            # Check if we have enough information for classification
            if len(session_data['responses']) >= self.min_questions:
                # Ask AI if we should classify now
                should_classify = self.ai_client.should_generate_classification(
                    content_analysis=session_data['content_analysis'],
                    responses=session_data['responses']
                )

                if should_classify or len(session_data['responses']) >= self.max_questions:
                    return None  # Trigger classification

            # Generate next question
            next_question = self.ai_client.generate_next_question(
                content_analysis=session_data['content_analysis'],
                previous_responses=session_data['responses']
            )

            # Update session data
            session_data['current_question'] = next_question
            self.cache.set_session(session_id, session_data)

            return next_question

        except Exception as e:
            logger.error(f"Error processing response: {e}")
            raise

    def get_session_data(self, session_id: str) -> Optional[Dict]:
        """Get session data from cache or database"""
        try:
            # Try cache first
            session_data = self.cache.get_session(session_id)
            if session_data:
                return session_data

            # Fall back to database
            session = UserSession.query.get(session_id)
            if not session:
                return None

            responses = [
                {'question': r.question, 'answer': r.answer}
                for r in session.responses
            ]

            session_data = {
                'url': session.url,
                'content_analysis': session.content_analysis,
                'responses': responses
            }

            # Update cache
            self.cache.set_session(session_id, session_data)

            return session_data
        except Exception as e:
            logger.error(f"Error getting session data: {e}")
            return None
