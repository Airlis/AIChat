from flask import request, jsonify
from flask_restx import Resource, fields
from app.api import api
from app.services.service_scraper import ScraperService
from app.services.service_response import ResponseService
from app.services.service_classification import ClassificationService
import uuid

# Define request and response models
scrape_model = api.model('Scrape', {
    'url': fields.String(required=True, description='URL to scrape')
})

option_model = api.model('Option', {
    'text': fields.String(required=True, description='Option text')
})

question_model = api.model('Question', {
    'questionText': fields.String(required=True, description='The question text'),
    'options': fields.List(fields.Nested(option_model), required=True, description='List of options')
})

questions_model = api.model('QuestionsResponse', {
    'questions': fields.List(fields.Nested(question_model), required=True)
})

answers_model = api.model('Answers', {
    'answers': fields.Raw(required=True, description='User answers')
})

results_model = api.model('Results', {
    'results': fields.String(description='Classification results')
})

@api.route('/scrape')
class ScrapeEndpoint(Resource):
    @api.expect(scrape_model)
    # @api.marshal_with(questions_model)
    def post(self):
        data = request.get_json()
        url = data.get('url')
        session_id = str(uuid.uuid4())

        if not url:
            return {'message': 'URL is required.'}, 400

        # Get questions using the ScraperService
        questions = ScraperService.get_questions(url)
        print(questions)
        if not questions:
            return {'message': 'No questions generated.'}, 500

        # Return questions and session ID in headers
        return {'questions': questions}, 200, {'Session-Id': session_id}

@api.route('/submit-answers')
class SubmitAnswersEndpoint(Resource):
    @api.expect(answers_model)
    @api.marshal_with(results_model)
    def post(self):
        data = request.get_json()
        answers = data.get('answers')
        session_id = request.headers.get('Session-Id')

        if not session_id:
            return {'message': 'Session ID is required'}, 400

        # Save responses using the ResponseService
        ResponseService.save_responses(session_id, answers)

        # Get classification using the ClassificationService
        classification = ClassificationService.get_classification(session_id, answers)

        return {'results': classification}, 200
