from app.extensions import db
from app.models import VisitorResponse

def save_responses(session_id, answers):
    for index, answer in answers.items():
        visitor_response = VisitorResponse(
            session_id=session_id,
            question=f"Question {index}",
            answer=answer
        )
        db.session.add(visitor_response)
    db.session.commit()
