from flask import jsonify, request
from app.api import api_blueprint as bp
from http import HTTPStatus
import logging
from app.services.service_scraper import ScraperService
from app.services.service_session import SessionService
from app.services.service_classification import ClassificationService
from flask_cors import cross_origin

logger = logging.getLogger(__name__)

@bp.route('/scrape', methods=['POST', 'OPTIONS'])
@cross_origin()
def scrape():
    """Start content analysis and classification session"""
    if request.method == 'OPTIONS':
        return '', 204

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

        session_id = session_service.create_session(url, content_data['analysis'], content_data['content_hash'])
        session_data = session_service.get_session_data(session_id)

        response = jsonify({
            'session_id': session_id,
            'question': content_data['first_question']['question'],
            'options': content_data['first_question']['options']
        })
        response.headers['Session-Id'] = session_id
        return response

    except Exception as e:
        logger.exception(f"Error in scrape endpoint: {str(e)}")
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/respond', methods=['POST', 'OPTIONS'])
@cross_origin()
def respond():
    """Process user response and get next question"""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), HTTPStatus.BAD_REQUEST

        session_id = request.headers.get('Session-Id')
        if not session_id:
            return jsonify({'error': 'Session-Id header is required'}), HTTPStatus.BAD_REQUEST

        answer = request.json.get('answer')
        if not answer:
            return jsonify({'error': 'Answer is required'}), HTTPStatus.BAD_REQUEST

        session_service = SessionService()
        classification_service = ClassificationService()
        
        next_question = session_service.process_response(session_id, answer)

        if not next_question:
            # Generate final classification
            classification = classification_service.generate_classification(session_id)
            return jsonify({'classification': classification})

        return jsonify({
            'question': next_question['question'],
            'options': next_question['options']
        })

    except Exception as e:
        logger.exception(f"Error in respond endpoint: {str(e)}")
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR