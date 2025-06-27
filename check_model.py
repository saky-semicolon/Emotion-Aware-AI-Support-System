import os

model_path = "app/ml_model/my_emotion_model.h5"
print("Looking for:", model_path)
print("Absolute path:", os.path.abspath(model_path))
print("Exists?", os.path.exists(model_path))
