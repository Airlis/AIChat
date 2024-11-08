from app.extensions import db

class VisitorResponse(db.Model):
    __tablename__ = 'visitor_responses'  # Explicitly set table name

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), nullable=False)
    question = db.Column(db.String, nullable=False)
    answer = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
