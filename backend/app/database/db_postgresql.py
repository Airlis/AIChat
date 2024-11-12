from typing import Dict, Optional, List
import logging
from datetime import datetime, timezone
from app.extensions import db
from app.models import UserSession, UserResponse, UserClassification

logger = logging.getLogger(__name__)

class PostgreSQL:
    def save_session(self, session_id: str, url: str, content_analysis: Dict) -> bool:
        """Create new user session"""
        try:
            session = UserSession(
                session_id=session_id,
                url=url,
                content_analysis=content_analysis,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(session)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            db.session.rollback()
            return False

    def save_response(self, session_id: str, question: str, answer: str) -> bool:
        """Save user response"""
        try:
            response = UserResponse(
                session_id=session_id,
                question=question,
                answer=answer,
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(response)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving response: {e}")
            db.session.rollback()
            return False

    def save_classification(self, session_id: str, interests: Dict) -> bool:
        """Save final classification"""
        try:
            classification = UserClassification(
                session_id=session_id,
                interests=interests,
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(classification)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving classification: {e}")
            db.session.rollback()
            return False

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data including responses"""
        try:
            session = UserSession.query.get(session_id)
            if not session:
                return None

            responses = [
                {
                    'question': r.question,
                    'answer': r.answer,
                    'timestamp': r.timestamp.isoformat()
                }
                for r in session.responses
            ]

            return {
                'session_id': session.session_id,
                'url': session.url,
                'content_analysis': session.content_analysis,
                'created_at': session.created_at.isoformat(),
                'responses': responses,
                'classification': session.classification.interests if session.classification else None
            }
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None

    def get_session_responses(self, session_id: str) -> List[Dict]:
        """Get all responses for a session"""
        try:
            responses = UserResponse.query.filter_by(session_id=session_id).all()
            return [
                {
                    'question': r.question,
                    'answer': r.answer,
                    'timestamp': r.timestamp.isoformat()
                }
                for r in responses
            ]
        except Exception as e:
            logger.error(f"Error getting responses: {e}")
            return []

    def get_classification(self, session_id: str) -> Optional[Dict]:
        """Get classification for a session"""
        try:
            classification = UserClassification.query.filter_by(session_id=session_id).first()
            if not classification:
                return None

            return {
                'interests': classification.interests,
                'timestamp': classification.timestamp.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting classification: {e}")
            return None
