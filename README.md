
# Emotion-Aware AI Complaint Management System

A smart, speech-driven university support platform that prioritizes student wellbeing using real-time emotion recognition and complaint triaging.

<img src="Documentation Page/medias/home.png" alt="Logo" width="100%"/>


## 1. Project Summary

The Emotion-Aware AI Complaint Management System is an intelligent web-based solution tailored for university students to submit voice-based complaints. The system utilizes a Convolutional Neural Network (CNN) for speech emotion recognition to assess emotional intensity and urgency of user-submitted audio. This allows university authorities to prioritize and address student concerns promptly, ensuring timely mental health and academic support interventions.

Through its emotion analysis, automated alerting system, interactive chatbot, report generation module, and administrative dashboard, the platform bridges communication gaps, improves complaint management, and fosters a more empathetic and effective student support system.

## 2. Demo Video

**Title:** Emotion-Aware AI Complaint System Demo 
**Link:** [Watch on YouTube](https://youtu.be/53eVlWif4LI)

## 3. Architecture Overview

<img src="Documentation Page/medias/architecture.png" alt="Architecture Diagram" width="30%"/>


## 4. Tech Stack

### 4.1 Backend
- **Python (Flask)** – Web framework for routing and API logic.
- **TensorFlow / Keras** – For training and deploying CNN-based emotion classification.
- **SQLAlchemy** – ORM for PostgreSQL integration.
- **Librosa, Noisereduce** – For audio feature extraction and noise processing.

### 4.2 Frontend
- **HTML5, CSS3 (Tailwind CSS)** – Semantic layout and modern UI.
- **JavaScript, Alpine.js** – Interactivity and state management.
- **ApexCharts & Chart.js** – Emotion visualizations.

### 4.3 Database
- **PostgreSQL** – Robust relational database.
- **Alembic** – For managing database migrations.

## 5. Setup Instructions

```bash
# 1. Clone the Repository
git clone https://github.com/saky-semicolon/Emotion-Aware-AI-Support-System.git
cd Emotion-Aware-AI-Support-System

# 2. Create Virtual Environment & Activate
python3 -m venv venv
source venv/bin/activate  # Linux
venv\Scripts\activate   # Windows

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Install FFmpeg (Required for Audio Conversion)
sudo apt install ffmpeg

# 5. Configure PostgreSQL & .env Variables
# DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, etc.

# 6. Apply Database Migrations
flask db upgrade

# 7. Run the Application
python run.py
```

## 6. API Endpoints

| Endpoint                  | Method | Description                                        |
|--------------------------|--------|----------------------------------------------------|
| `/api/predict`           | POST   | Accepts audio and returns predicted emotion        |
| `/api/respond`           | POST   | Sends automated bot-like response (if enabled)     |
| `/download_report/<id>`  | GET    | Download the PDF emotion report for complaint      |
| `/admin/*`               | GET    | Admin dashboard, complaint and alert management    |


## 7.1 Student Features

- **Homepage** – Emotion-aware branding and call-to-action.
- **Registration & Login** – With image upload and input validation.
- **Dashboard** – Emotional bar charts and emoji analysis.
- **Complaint Submission** – Audio/text with status tracking.
- **Chatbot** – Simulated emotional replies based on tone.
- **Report Downloads** – PDF with transcript, emotional data, metadata.
- **Profile Management** – Editable user info and profile photo.

## 7.2 Admin Features

- **Login** – Secure panel login for authorized staff.
- **Dashboard** – Emotion analytics and complaint statistics.
- **Complaint Management** – View/update statuses and add remarks.
- **Alerts & Notifications** – Real-time emotional triggers and complaint updates.

## 8. Model Details

- **Model Type:** CNN (Convolutional Neural Network)
- **Trained On:** MFCC + ZCR + RMSE features from annotated speech datasets
- **Outputs:** Multiclass emotion prediction (Happy, Sad, Angry, Fear, Neutral)
- **File:** `my_emotion_model.h5`
- **Preprocessors:** StandardScaler, OneHotEncoder


## 9. Contribution Guide

1. Fork the repository
2. Clone it locally and set up environment
3. Create a feature branch
4. Submit a pull request with description
5. Follow coding standards and commit guidelines

## 10. License

**MIT License**

```text
MIT License

Copyright (c) 2025
S M Asiful Islam Saky, Rania Kherba, Ahmed Dugje Kadiri

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:
```

## 11. Authors & Contact

- [**S M Asiful Islam Saky**](https://saky.space)
- **Rania Kherba**
- **Ahmed Dugje Kadiri**

> ⭐ Star this repo to support the project and inspire more emotion-aware AI systems for social impact!
