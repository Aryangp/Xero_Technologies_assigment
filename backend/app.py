from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from pydub import AudioSegment
from io import BytesIO
import base64

app = Flask(__name__)
auth = HTTPBasicAuth()
CORS(app, resources={r"/process_audio": {"origins": "*"}})
# In-memory user database for demo purposes of creating user normally this would be a database
users = {}

# Audio stream processing route (speed up the audio by 2x)
@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        file = request.files.get('audio')

        if not name or not email:
            return jsonify({'error': 'Name and email are required'}), 400
        
        if not file:
            return jsonify({'error': 'No audio file provided'}), 400

        # Debug: Check the file content type and name
        print(f"Received file: {file.filename}, Content-Type: {file.content_type}")

        # Convert the file to an AudioSegment
        audio_segment = AudioSegment.from_file(file, format="wav")

        # Debug: Check the duration of the audio segment
        print(f"Audio segment duration (ms): {len(audio_segment)}")

        # Speed up the audio (2x)
        sped_up_audio = audio_segment.speedup(playback_speed=2.0)

        # Debug: Check the duration of the sped-up audio segment
        print(f"Sped-up audio duration (ms): {len(sped_up_audio)}")

        # Export the sped-up audio to a byte buffer
        output_buffer = BytesIO()
        sped_up_audio.export(output_buffer, format="wav")
        output_buffer.seek(0)

        # Debug: Check the size of the output buffer
        base64_data_uri = base64.b64encode(output_buffer.read()).decode()

        # Return the Base64 Data URI to the frontend
        return base64_data_uri
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User signup route
@app.route('/signup', methods=['POST'])
def signup():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if username in users:
        return jsonify({'error': 'User already exists'}), 400

    users[username] = password
    return jsonify({'message': 'User created successfully'}), 201

# User login route
@app.route('/login', methods=['POST'])
@auth.login_required
def login():
    return jsonify({'message': 'Login successful'}), 200

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return True
    return False

if __name__ == '__main__':
    app.run(debug=True)
