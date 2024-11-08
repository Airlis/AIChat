from app.database.db_postgresql import save_responses

class ResponseService:
    @staticmethod
    def save_responses(session_id, answers):
        save_responses(session_id, answers)
