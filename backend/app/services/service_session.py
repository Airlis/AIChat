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
        self.max_questions = 5  # Maximum number of questions before classification

    def create_session(self, url: str, content_analysis: Dict) -> str:
        """Create new session and generate first question"""
        try:
            session_id = str(uuid4())
            
            # Save to database
            if not self.db.save_session(session_id, url, content_analysis):
                raise Exception("Failed to save session")

            # Generate first question
            try:
                question = self.ai_client.generate_next_question(
                    content_analysis=content_analysis
                )
            except Exception as e:
                logger.error(f"Error generating question: {e}")
                question = {
                    "question": "What interests you about this website?",
                    "options": [
                        "Products and Features",
                        "Company Information",
                        "Support and Help",
                        "Other"
                    ]
                }

            # Cache session data
            session_data = {
                'url': url,
                'content_analysis': content_analysis,
                'current_question': question,
                'responses': []
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

            # Save current response
            current_question = session_data['current_question']
            session_data['responses'].append({
                'question': current_question['question'],
                'answer': answer
            })
            
            # Check if we have enough information for classification
            if len(session_data['responses']) >= 2:  # At least 2 responses
                # Ask AI if we should classify now
                should_classify = self.ai_client.should_generate_classification(
                    content_analysis=session_data['content_analysis'],
                    responses=session_data['responses']
                )
                
                if should_classify:
                    return None  # Trigger classification

            # Continue with next question if needed
            if len(session_data['responses']) >= self.max_questions:
                return None

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
