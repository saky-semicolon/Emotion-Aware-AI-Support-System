import requests

url = "http://localhost:5000/api/predict"
file_path = "tamanna.wav"  # Change this to your .wav file

files = {'file': open(file_path, 'rb')}
data = {'user_id': '1'}  # Replace with valid user_id


# Simulated user ID
user_id = 6

# Create form data
with open(file_path, 'rb') as f:
    files = {'file': ('test.wav', f, 'audio/wav')}
    data = {'user_id': str(user_id)}
    response = requests.post(url, files=files, data=data)

# Print response
print("Status Code:", response.status_code)

