from app.utils.scraper import scrape_content
from app.utils.ai_client import analyze_content, generate_questions
from app.caching.cache_redis import get_cached_questions, cache_questions
from app.database.db_dynamodb import get_cached_content, cache_content

class ScraperService:
    @staticmethod
    def get_questions(url):
        # Check Redis cache for questions
        questions = get_cached_questions(url)
        if questions:
            return questions

        # Check DynamoDB for cached content
        content, last_modified, etag = get_cached_content(url)
        if not content or not ScraperService.is_content_up_to_date(url, last_modified, etag):
            # Scrape content and cache it
            content, last_modified, etag = scrape_content(url)
            if not content:
                print("Failed to scrape content.")
                return None
            cache_content(url, content, last_modified, etag)

        # Analyze content and generate questions
        topics = analyze_content(content)
        if topics:
            questions = generate_questions(topics)
            if questions:
                # Cache questions in Redis
                cache_questions(url, questions)
            else:
                print("No questions generated from topics.")
                return None
        else:
            print("No topics generated from content.")
            return None

        return questions

    @staticmethod
    def is_content_up_to_date(url, last_modified, etag):
        import requests
        headers = {}
        if last_modified:
            headers['If-Modified-Since'] = last_modified
        if etag:
            headers['If-None-Match'] = etag

        response = requests.head(url, headers=headers)
        return response.status_code == 304
