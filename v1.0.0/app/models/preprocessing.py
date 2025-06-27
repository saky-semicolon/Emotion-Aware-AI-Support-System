from app.extensions import db
from datetime import datetime

class AudioRec(db.Model):
    __tablename__ = 'audio_rec'
    __table_args__ = (
        # Composite index on user_id + upload_time
        db.Index('idx_user_uploads', 'user_id', 'upload_time'),  
        
        # Index on processing_status for faster filtering
        db.Index('idx_processing_status', 'processing_status'),
    )
    rec_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    processing_status = db.Column(db.String(50), default='pending')  # pending/completed/failed
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    transcription_status = db.Column(db.String(50))  #pending/completed/failed
    # Relationships
    preprocessing = db.relationship('PreprocessingResults', backref='recording', uselist=False)
    features = db.relationship('FeatureVectors', backref='recording', uselist=False)
    detections = db.relationship('DetectionResults', backref='recording')

class PreprocessingResults(db.Model):
    __tablename__ = 'preprocessing_results'
    prepro_id = db.Column(db.Integer, primary_key=True)
    rec_id = db.Column(db.Integer, db.ForeignKey('audio_rec.rec_id'), nullable=False, index=True)
    noise_red = db.Column(db.Boolean, default=False)
    sampling_rate = db.Column(db.Integer)
    features_extracted = db.Column(db.Boolean, default=False)
    prepro_time = db.Column(db.Float)  # Processing time in seconds
    error_message = db.Column(db.Text)

class FeatureVectors(db.Model):
    __tablename__ = 'feature_vectors'
    feature_id = db.Column(db.Integer, primary_key=True)
    rec_id = db.Column(db.Integer, db.ForeignKey('audio_rec.rec_id'), nullable=False, index=True)
    mfcc = db.Column(db.JSON)  # Mel-frequency cepstral coefficients
    rmse = db.Column(db.Float)  # Root Mean Square Energy
    zcr = db.Column(db.Float)  # Zero Crossing Rate