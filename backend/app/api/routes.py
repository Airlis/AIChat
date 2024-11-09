from flask import jsonify, request
from app.api import api_blueprint as bp
from http import HTTPStatus
import logging
from app.services.service_scraper import ScraperService
from app.services.service_session import SessionService
from app.services.service_classification import ClassificationService

logger = logging.getLogger(__name__)

@bp.route('/scrape', methods=['POST'])
def scrape():
    """Start content analysis and classification session"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), HTTPStatus.BAD_REQUEST
            
        url = request.json.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), HTTPStatus.BAD_REQUEST

        scraper_service = ScraperService()
        session_service = SessionService()

        content_data = scraper_service.process_url(url)
        if not content_data:
            return jsonify({'error': 'Failed to process URL'}), HTTPStatus.BAD_REQUEST

        session_id = session_service.create_session(url, content_data['analysis'])
        session_data = session_service.get_session_data(session_id)

        return jsonify({
            'session_id': session_id,
            'question': session_data['current_question']['question'],
            'options': session_data['current_question']['options']
        })

    except Exception as e:
        # This will log the full traceback
        logger.exception(f"Error in scrape endpoint: {str(e)}")
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/respond', methods=['POST'])
def respond():
    """Process user response and get next question"""
    try:
        session_id = request.json.get('session_id')
        answer = request.json.get('answer')

        session_service = SessionService()
        next_question = session_service.process_response(session_id, answer)

        if not next_question:
            # Generate final classification
            classification_service = ClassificationService()
            classification = classification_service.generate_classification(session_id)
            return jsonify(classification)

        return jsonify({
            'session_id': session_id,
            'question': next_question['question'],
            'options': next_question['options']
        })

    except Exception as e:
        logger.error(f"Error in response endpoint: {e}")
        return jsonify({'message': 'Internal server error'}), HTTPStatus.INTERNAL_SERVER_ERROR 