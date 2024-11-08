from app.utils.ai_client import generate_classification
from app.caching.cache_redis import get_cached_classification, cache_classification

class ClassificationService:
    @staticmethod
    def get_classification(session_id, answers):
        # Check Redis cache for classification
        classification = get_cached_classification(session_id)
        if classification:
            return classification

        # Generate classification
        classification = generate_classification(answers)

        # Cache classification in Redis
        cache_classification(session_id, classification)

        return classification
