import numpy as np
import librosa
import noisereduce as nr
import joblib
from tensorflow.keras.models import load_model
import speech_recognition as sr
from fpdf import FPDF
import os
from datetime import datetime
from app.models.preprocessing import AudioRec, PreprocessingResults, FeatureVectors
from app.models.detection import MLModel, DetectionResults
from app.models.cases_management import Complaint  # Import Complaint model for report generation   
from app.models.users import User , StudentProfile  # Import StudentProfile model for student data


# Load model and preprocessors
model = load_model('app/ml_model/my_emotion_model.h5')
scaler = joblib.load('app/ml_model/standard_scaler.pkl')
encoder = joblib.load('app/ml_model/onehot_encoder.pkl')


# === Noise Handling ===
def reduce_noise(data, sr):
    noise_clip = data[:int(sr * 0.5)]
    return nr.reduce_noise(y=data, sr=sr, y_noise=noise_clip, prop_decrease=1.0)

def is_noisy(data, sr, flatness_threshold=0.05, rms_threshold=0.01):
    spectral_flat = np.mean(librosa.feature.spectral_flatness(y=data))
    rms = np.mean(librosa.feature.rms(y=data))
    return spectral_flat > flatness_threshold and rms < rms_threshold


# === Feature Extraction ===
def zcr(data, frame_length, hop_length):
    return np.squeeze(librosa.feature.zero_crossing_rate(data, frame_length=frame_length, hop_length=hop_length))

def rmse(data, frame_length=2048, hop_length=512):
    return np.squeeze(librosa.feature.rms(y=data, frame_length=frame_length, hop_length=hop_length))

def mfcc(data, sr, frame_length=2048, hop_length=512, flatten=True):
    mfcc_result = librosa.feature.mfcc(y=data, sr=sr, n_fft=frame_length, hop_length=hop_length)
    return np.squeeze(mfcc_result.T) if not flatten else np.ravel(mfcc_result.T)

def extract_features(data, sr=22050, frame_length=2048, hop_length=512):
    return np.hstack((
        zcr(data, frame_length, hop_length),
        rmse(data, frame_length, hop_length),
        mfcc(data, sr, frame_length, hop_length)
    ))


# === Helper: Process one chunk ===
def process_chunk(data, sr, expected_shape=(1, 2376)):
    if is_noisy(data, sr):
        data = reduce_noise(data, sr)

    res = extract_features(data, sr=sr)

    # Ensure shape match
    flat_size = np.prod(expected_shape)
    if res.size < flat_size:
        res = np.pad(res, (0, flat_size - res.size), mode='constant')
    else:
        res = np.resize(res, flat_size)

    i_result = scaler.transform(res.reshape(1, -1))
    return np.expand_dims(i_result, axis=2)


# === NEW: Chunk audio into 2.5s slices ===
def chunk_audio(data, sr, chunk_duration=2.5):
    chunk_samples = int(sr * chunk_duration)
    return [data[i:i+chunk_samples] for i in range(0, len(data), chunk_samples) if len(data[i:i+chunk_samples]) == chunk_samples]

# === Optional: Raw feature return ===
def extract_all_features(path, sr=22050, frame_length=2048, hop_length=512):
    data, sample_rate = librosa.load(path, sr=sr, duration=2.5, offset=0.6)

    if is_noisy(data, sample_rate):
        data = reduce_noise(data, sample_rate)

    zcr_feat = zcr(data, frame_length, hop_length)
    rmse_feat = rmse(data, frame_length, hop_length)
    mfcc_feat = mfcc(data, sample_rate, frame_length, hop_length, flatten=False)

    return {
        'zcr': zcr_feat.tolist(),
        'rmse': rmse_feat.tolist(),
        'mfcc': mfcc_feat.tolist()
    }


# === UPDATED: Predict on long audio by averaging over chunks ===
def prediction(path):
    data, sr = librosa.load(path, sr=None)
    chunks = chunk_audio(data, sr)

    if not chunks:
        return {
            "primary_emo": None,
            "detected_emos": {},
            "mean_rmse": 0.0,
            "mean_zcr": 0.0,
            "error": "Audio too short for chunking."
        }


    label_names = list(encoder.categories_[0])
    all_confidences = np.zeros(len(label_names))

    rmse_means = []
    zcr_means = []

    for chunk in chunks:
        # Just calculate means here — no change to model input
        rmse_means.append(np.mean(rmse(chunk)))
        zcr_means.append(np.mean(zcr(chunk, frame_length=2048, hop_length=512)))

        # Model input and prediction stay the same as before
        res = process_chunk(chunk, sr)
        pred = model.predict(res)[0]
        all_confidences += pred

    # Average model confidence and mean features
    avg_confidences = all_confidences / len(chunks)
    rmse_scalar = float(np.mean(rmse_means))
    zcr_scalar = float(np.mean(zcr_means))

    # Prepare result confidence list
    confidence_scores = []
    for idx, label in enumerate(label_names):
        score = avg_confidences[idx]
        score = 0 if score < 0.001 else score
        confidence_scores.append({'label': label, 'confidence': score})

    sorted_confidence_scores = sorted(confidence_scores, key=lambda x: x['confidence'], reverse=True)

    # Here you can store rmse_scalar and zcr_scalar in DB if needed

    print(f"\nPredicted Emotion: {sorted_confidence_scores[0]['label']}")
    print(f"Mean RMSE: {rmse_scalar}, Mean ZCR: {zcr_scalar}")

    return {
        "primary_emo": sorted_confidence_scores[0]['label'],
        "detected_emos": {item['label']: item['confidence'] for item in sorted_confidence_scores},
        "mean_rmse": rmse_scalar,
        "mean_zcr": zcr_scalar
    }


# === Main Prediction Function ===
def predict_emotion(audio_path):
    data, sr = librosa.load(audio_path, sr=None)
    processed_data = process_chunk(data, sr)
    prediction = model.predict(processed_data)
    predicted_label = encoder.inverse_transform(prediction > 0.5)
    return predicted_label[0][0]


# === Transcription ===
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand audio."
    except sr.RequestError:
        return "Speech recognition service failed."


# === PDF Report Generation ===

def generate_report(audio_path, student_profile, detection_result, complaint, report_path):
    try:
        emotion = detection_result.primary_emo or "Unknown"
        transcript = transcribe_audio(audio_path)

        pdf = FPDF()
        pdf.add_page()

        # Set document margins
        pdf.set_margins(left=15, top=10, right=15)
        pdf.set_auto_page_break(auto=True, margin=10)

        # Add University Logo
        logo_path = os.path.join(os.getcwd(), 'app', 'static', 'images', 'logo.png')
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=(210 - 40) / 2, y=10, w=40)
        pdf.ln(22)

        # Title
        pdf.set_font("Helvetica", 'B', 20)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "EMOTION DETECTION REPORT", ln=True, align='C')
        pdf.ln(5)

        # Metadata
        pdf.set_font("Helvetica", '', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
        pdf.ln(10)
        pdf.set_text_color(0, 0, 0)

        # Section title helper
        def draw_section_title(title):
            heading_blue = (44, 62, 105)
            pdf.set_font("Helvetica", 'B', 13)
            pdf.set_text_color(*heading_blue)
            pdf.cell(0, 6, title, ln=True)
            pdf.set_draw_color(*heading_blue)
            pdf.set_line_width(0.5)
            x = pdf.get_x()
            y = pdf.get_y()
            pdf.line(x, y, x + 180, y)
            pdf.ln(6)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", '', 11)

        # STUDENT INFORMATION
        draw_section_title("STUDENT INFORMATION")
        dept_name = getattr(student_profile.department, 'dept_name', 'N/A')
        col_width = 85
        line_height = 7

        def info_row(label, value, indent=0):
            pdf.set_font("Helvetica", 'B', 11)
            pdf.cell(col_width + indent, line_height, label)
            pdf.set_font("Helvetica", '', 11)
            pdf.cell(col_width, line_height, str(value or "N/A"), ln=True)

        info_row("Full Name:", student_profile.full_name)
        info_row("ID Number:", student_profile.id_number)
        info_row("Gender:", student_profile.gender)
        info_row("Academic Year:", student_profile.academic_year)
        info_row("Department:", dept_name)
        info_row("Phone:", student_profile.phone)
        info_row("User ID:", student_profile.user_id)
        pdf.ln(8)

        # COMPLAINT DETAILS
        draw_section_title("COMPLAINT DETAILS")
        info_row("Complaint ID:", complaint.complaint_id)
        info_row("Submit Date:", complaint.submit_date.strftime('%Y-%m-%d %H:%M'))
        info_row("Priority Level:", complaint.priority_level)
        info_row("Primary Emotion:", emotion.title())
        pdf.ln(8)

        # Check space before table
        if pdf.get_y() + 30 > 270:
            pdf.add_page()
            pdf.set_y(20)

        # EMOTION ANALYSIS
        draw_section_title("EMOTION ANALYSIS")
        heading_blue = (44, 62, 105)
        pdf.set_draw_color(*heading_blue)
        pdf.set_fill_color(*heading_blue)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", 'B', 11)
        pdf.cell(100, 8, "EMOTION", border=1, align='C', fill=True)
        pdf.cell(80, 8, "CONFIDENCE SCORE", border=1, align='C', fill=True, ln=True)

        # Table rows
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", '', 10)
        row_height = 7

        if hasattr(detection_result, 'detected_emos') and detection_result.detected_emos:
            sorted_emotions = sorted(
                detection_result.detected_emos.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for idx, (emo, score) in enumerate(sorted_emotions):
                fill_color = (245, 247, 255) if idx % 2 == 0 else (255, 255, 255)
                pdf.set_fill_color(*fill_color)
                pdf.cell(100, row_height, emo.title(), border='LR', align='C', fill=True)
                pdf.cell(80, row_height, f"{float(score):.1f}%", border='LR', align='C', fill=True, ln=True)
        else:
            pdf.set_fill_color(255, 255, 255)
            pdf.cell(180, row_height, "No emotion analysis data available", border=1, align='C', ln=True, fill=True)

        # Bottom border of table
        pdf.set_draw_color(*heading_blue)
        pdf.cell(100, 0, '', border='T')
        pdf.cell(80, 0, '', border='T', ln=True)
        pdf.ln(8)

        # AUDIO TRANSCRIPTION
        draw_section_title("AUDIO TRANSCRIPTION")
        pdf.set_font("Helvetica", '', 10)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 6, transcript or "No transcription available.", align='L')
        pdf.ln(5)

        # Footer
        pdf.set_y(-12)
        pdf.set_font("Helvetica", 'I', 7)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, "Confidential - For official use only", align='C')

        # Save report
        pdf.output(report_path)

        if not os.path.exists(report_path):
            raise FileNotFoundError("PDF was not created.")

        return {
            "emotion": emotion,
            "transcription": transcript,
            "report_path": report_path
        }

    except Exception as e:
        import logging
        logging.error(f"Error generating report: {e}", exc_info=True)
        raise
