from datetime import datetime, timezone
from app.extensions import db

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    session_id = db.Column(db.String(36), primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    content_analysis = db.Column(db.JSON)
    
    responses = db.relationship('UserResponse', backref='session', lazy=True)
    classification = db.relationship('UserClassification', backref='session', uselist=False)

class UserResponse(db.Model):
    __tablename__ = 'user_responses'
    
    response_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('user_sessions.session_id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class UserClassification(db.Model):
    __tablename__ = 'user_classifications'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('user_sessions.session_id'), nullable=False)
    interests = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))