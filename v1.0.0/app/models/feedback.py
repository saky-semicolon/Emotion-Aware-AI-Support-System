from app.extensions import db
from datetime import datetime

class UserFeedback(db.Model):
    __tablename__ = 'user_feedback'
    __table_args__ = (
    db.Index('idx_feedback_complaint', 'complaint_id', 'rating'),
)
    feedback_id = db.Column(db.Integer, primary_key=True)
    rec_id = db.Column(db.Integer, db.ForeignKey('audio_rec.rec_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.complaint_id'), nullable=True)  # Made nullable
    
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text)
    feedback_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Corrected relationships
    recording = db.relationship('AudioRec', backref='feedbacks')
    complaint = db.relationship('Complaint', backref='feedbacks')
    user = db.relationship('User', backref='feedbacks')


class ChatResponse(db.Model):
    __tablename__ = 'chat_response'
    response_id = db.Column(db.Integer, primary_key=True)
    rec_id = db.Column(db.Integer, db.ForeignKey('audio_rec.rec_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    resp_type = db.Column(db.String(50))
    resp_text = db.Column(db.Text)
    resp_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    follow_up_req = db.Column(db.Boolean, default=False)