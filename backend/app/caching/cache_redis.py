from app.extensions import cache

def get_cached_questions(url):
    try:
        return cache.get(f"questions:{url}")
    except Exception as e:
        print(f"Error fetching questions from Redis: {e}")
        return None

def cache_questions(url, questions):
    if questions:
        try:
            cache.set(f"questions:{url}", questions, timeout=3600)
        except Exception as e:
            print(f"Error caching questions in Redis: {e}")
    else:
        print("No questions to cache.")

def get_cached_classification(session_id):
    try:
        return cache.get(f"classification:{session_id}")
    except Exception as e:
        print(f"Error fetching classification from Redis: {e}")
        return None

def cache_classification(session_id, classification):
    try:
        cache.set(f"classification:{session_id}", classification, timeout=3600)
    except Exception as e:
        print(f"Error caching classification in Redis: {e}")
