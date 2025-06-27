from app.extensions import db
from datetime import datetime


class MLModel(db.Model):
    __tablename__ = 'ml_model'
    model_id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    model_type = db.Column(db.String(50))
    version = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    activated_at = db.Column(db.DateTime)
    storage_path = db.Column(db.String(255))
    accuracy = db.Column(db.Float)
    detections = db.relationship('DetectionResults', backref='model')

class DetectionResults(db.Model):
    __tablename__ = 'detection_results'
    __table_args__ = (
    db.Index('idx_primary_emo', 'primary_emo'),
    db.Index('idx_severity', 'severity_level'),
    db.Index('idx_detect_user', 'user_id', 'detect_id'),
    db.Index('idx_detect_rec', 'rec_id'),
)
    detect_id = db.Column(db.Integer, primary_key=True)
    rec_id = db.Column(db.Integer, db.ForeignKey('audio_rec.rec_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    primary_emo = db.Column(db.String(50))
    detected_emos = db.Column(db.JSON)
    severity_level = db.Column(db.String(20))
    model_id = db.Column(db.Integer, db.ForeignKey('ml_model.model_id'))
    error_message = db.Column(db.Text)
    complaint = db.relationship('Complaint', backref='detection', uselist=False)
    alerts = db.relationship('PriorityAlert', backref='detection')

