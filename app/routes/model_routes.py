import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from app.ml_model.preprocess import prediction, extract_all_features, generate_report
from app.extensions import db
from app.models.preprocessing import AudioRec, PreprocessingResults, FeatureVectors
from app.models.detection import MLModel, DetectionResults
from app.models.cases_management import Complaint  # ✅ Import Complaint model
from flask_cors import CORS
import numpy as np
from app.models.users import User, StudentProfile
import subprocess
from uuid import uuid4
from app.models.cases_management import PriorityAlert, Notification  # ✅ Required for alert creation


api_bp = Blueprint('model_api', __name__, url_prefix='/api')
CORS(api_bp, resources={
    r"/predict": {"origins": "*"},
    r"/respond": {"origins": "*"},
    r"/download_report/*": {"origins": "*"}
})

# Configuration
ALLOWED_EXTENSIONS = {'wav', 'webm', 'ogg', 'mp4', 'mpeg', 'mp3'}
UPLOAD_FOLDER = 'uploads'
REPORT_FOLDER = 'reports'
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# Load model once at startup
try:
    model = load_model("app/ml_model/my_emotion_model.h5")
except Exception as e:
    logging.error(f"Failed to load ML model: {str(e)}")
    raise RuntimeError("Could not initialize ML model")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_audio_to_wav(input_path, output_path):
    try:
        subprocess.run([
            'ffmpeg', '-i', input_path,
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '1',
            output_path
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error("Audio conversion failed: %s", str(e))
        return False
    except Exception as e:
        logging.error(f"Audio conversion failed: {str(e)}")
        return False
 
@api_bp.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({
            'status': 'error',
            'error': 'Invalid file type',
            'allowed_types': list(ALLOWED_EXTENSIONS)
        }), 400

    try:
        user_id = int(request.form.get('user_id', 0))
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'error': 'Invalid user ID format'}), 400

    # === Step 1: Generate Timestamp-Based Filenames ===
    timestamp_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    temp_filename = f"user_{user_id}_{timestamp_str}.{file_ext}"
    temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)

    # === Step 2: Save Original File ===
    try:
        file.save(temp_path)
        logging.info(f"✅ File saved: {temp_path}")
    except Exception as e:
        logging.error(f"❌ Failed to save uploaded file: {e}")
        return jsonify({'status': 'error', 'error': 'File save failed'}), 500

    # === Step 3: Convert to .wav if needed ===
    wav_filename = f"user_{user_id}_{timestamp_str}.wav"
    wav_path = os.path.join(UPLOAD_FOLDER, wav_filename)
    final_path = wav_path if file_ext != 'wav' else temp_path

    if file_ext != 'wav':
        if not convert_audio_to_wav(temp_path, wav_path):
            os.remove(temp_path)
            return jsonify({'status': 'error', 'error': 'Audio conversion failed'}), 500
        os.remove(temp_path)

    # === Step 4: Check Audio Exists ===
    if not os.path.exists(final_path):
        logging.error(f"❌ Final audio file not saved: {final_path}")
        return jsonify({'status': 'error', 'error': 'Audio file not saved'}), 500

    # === Step 5: Save Audio Record ===
    audio_rec = AudioRec(user_id=user_id, processing_status='pending', upload_time=datetime.utcnow())
    db.session.add(audio_rec)
    db.session.commit()

    try:
        # === Step 6: Emotion Detection ===
        detailed_features = extract_all_features(final_path)
        results = prediction(final_path)

        # === Step 7: Type Conversion ===
        def convert_types(obj):
            if isinstance(obj, np.ndarray): return obj.tolist()
            elif isinstance(obj, np.generic): return obj.item()
            return obj

        detailed_features = {k: convert_types(v) for k, v in detailed_features.items()}
        results = results[0] if isinstance(results, list) and len(results) > 0 else results
        results = {k: convert_types(v) for k, v in results.items()}

        # === Step 8: Save Detection Results ===
        detection = DetectionResults(
            rec_id=audio_rec.rec_id,
            user_id=user_id,
            primary_emo=results['primary_emo'],
            detected_emos=results['detected_emos']
        )
        db.session.add(detection)
        db.session.flush()

        # === Step 9: Save Complaint ===
        emo = results['primary_emo'].lower()
        priority = 'high' if emo in ['angry', 'fear', 'sad'] else 'medium' if emo == 'neutral' else 'low'
        complaint = Complaint(
            detect_id=detection.detect_id,
            user_id=user_id,
            priority_level=priority,
            complaint_status='open'
        )
        db.session.add(complaint)
        db.session.flush()

        # === Step 10: Save Alert & Notification ===
        db.session.add(PriorityAlert(
            detect_id=detection.detect_id,
            alert_status='active',
            alert_timestamp=datetime.utcnow()
        ))
        db.session.add(Notification(
            user_id=user_id,
            complaint_id=complaint.complaint_id,
            message=f"A high-priority complaint has been detected with emotion: {results['primary_emo']}",
            sent_at=datetime.utcnow(),
            read_status=False
        ))

        # === Step 11: Generate Report ===
        report_filename = f"report_{user_id}_{timestamp_str}.pdf"
        report_path = os.path.join(REPORT_FOLDER, report_filename)
        student_profile = StudentProfile.query.filter_by(user_id=user_id).first()

        if not student_profile:
            raise Exception("Student profile not found")

        generate_report(final_path, student_profile, detection, complaint, report_path)

        # === Step 12: Finalize ===
        audio_rec.processing_status = 'processed'
        db.session.commit()

        return jsonify({
            "status": "success",
            "prediction": results["primary_emo"],
            "emotion": results["primary_emo"],
            "confidence_scores": results["detected_emos"],
            "mean_zcr": results.get("mean_zcr"),
            "mean_rmse": results.get("mean_rmse"),
            "report_url": f"/download_report/{report_filename}",
            "recording_id": audio_rec.rec_id,
            "complaint_id": complaint.complaint_id
        }), 200

    except Exception as e:
        audio_rec.processing_status = 'failed'
        db.session.commit()
        if os.path.exists(final_path):
            os.remove(final_path)
        logging.error(f"❌ Processing error: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'error': 'Processing failed', 'message': str(e)}), 500
