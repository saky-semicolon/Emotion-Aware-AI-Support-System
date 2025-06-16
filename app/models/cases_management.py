from app.extensions import db
from datetime import datetime
from sqlalchemy import Enum
from sqlalchemy import text 


class Complaint(db.Model):
    __tablename__ = 'complaint'
    complaint_id = db.Column(db.Integer, primary_key=True)
    detect_id = db.Column(db.Integer, db.ForeignKey('detection_results.detect_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    priority_level = db.Column(
    Enum('low', 'medium', 'high', name='priority_level_enum'),
    nullable=True)
    submit_date = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    complaint_status = db.Column(
        Enum('open', 'in_progress', 'resolved', 'closed', name='complaint_status_enum'),
    default='open')
    actions = db.Column(db.Text)
    report = db.relationship('CaseReport', backref='complaint', uselist=False)
    history = db.relationship('CaseHistory', backref='complaint')
    notifications = db.relationship('Notification', backref='complaint')

class CaseReport(db.Model):
    __tablename__ = 'case_report'
    report_id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.complaint_id'), nullable=False)
    content = db.Column(db.Text)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    recommendations = db.Column(db.Text)
    pdf_generated = db.Column(db.Boolean, default=False)

class CaseHistory(db.Model):
    __tablename__ = 'case_history'
    history_id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.complaint_id'), nullable=False, index=True)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), index=True)
    field_changed = db.Column(db.String(50))
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    change_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

class PriorityAlert(db.Model):
    __tablename__ = 'priority_alert'
    __table_args__ = (
    db.Index('idx_alert_status', 'alert_status', 'alert_timestamp'),
)
    alert_id = db.Column(db.Integer, primary_key=True)
    detect_id = db.Column(db.Integer, db.ForeignKey('detection_results.detect_id'), nullable=False)
    alert_status = db.Column(
    Enum('active', 'read', name='alert_status_enum'),
    default='active')
    alert_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    __table_args__ = (
    db.Index('idx_notification_timeline', 'user_id', 'sent_at'),
)
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.complaint_id'))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.Column(db.Text, nullable=False)
    read_status = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)