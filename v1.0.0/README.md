# 🎧 Emotion-Aware AI Support System

An AI-powered web application that listens to student voice inputs, detects their emotions using deep learning models, classifies the emotion intensity, and provides real-time responses and case management. This system is designed to support mental health monitoring and ensure prompt intervention for high-priority emotional states.
![image](https://github.com/user-attachments/assets/1bda46d5-b8b7-49dc-b409-be2c13ea3333)


## 🧠 Project Overview

This project integrates machine learning, speech recognition, and emotion analysis to build a student support tool. The system performs the following core functions:

- Detects emotions from voice input using LSTM/CNN
- Classifies emotion intensity (High, Mid, Low) using Logistic Regression
- Prioritizes emotional cases via a priority queue
- Responds using rule-based or AI-driven chatbot logic
- Logs and manages cases in a database
- Supports optional alerts and report generation
- Visualizes emotion trends and system performance


## 📸 Project Demo

> 🎥 Coming Soon — will include a walkthrough of the full system including voice input, emotion classification, and chatbot interaction.


## 🔧 Features

- 🎙️ **Emotion Detection**: Converts student speech into text and detects underlying emotions using deep learning.
- 📊 **Intensity Classification**: Categorizes detected emotions into High, Mid, or Low severity using Logistic Regression.
- ⏳ **Priority Queue**: Automatically sorts and processes cases based on emotional urgency.
- 🤖 **Chatbot Interaction**: Engages with students via text-based follow-up and support using rule-based or GPT AI models.
- 🗃️ **Case Management**: Tracks emotional cases from start to resolution.
- 📢 **Alerts & Notifications** *(optional)*: Sends real-time alerts for urgent cases via email/SMS.
- 📈 **Analytics Dashboard** *(in progress)*: Visualizes emotion trends and performance metrics.
- 🔒 **Security**: Role-based access control (RBAC) and secure login for authorized users.
- 📝 **Reports & Recommendations** *(optional)*: Summarizes emotional data and suggests action.


## 🛠️ Tech Stack

| Area                | Technology               |
|---------------------|---------------------------|
| Frontend            | HTML5, CSS3, JavaScript   |
| Backend             | Python (Flask), Flask-CORS|
| Machine Learning    | TensorFlow / Keras, Scikit-learn |
| Audio Processing    | LibROSA, SpeechRecognition, VOSK |
| Database            | SQLite (or MySQL for production) |
| Deployment *(future)*| Render / Railway / Heroku |
| Notification APIs   | Twilio / SMTP (optional)  |


## 🤝 Contributors

| Name           | Role                          |
|----------------|-------------------------------|
| S M Asiful Islam Saky    | Database Integration, Backend |
| Rania Kherba  | Deep Learning Model Development            |
| Ahmed Dugje Kadiri  | Front-end Part  |
