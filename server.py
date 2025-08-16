# filename: server.py

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask application
app = Flask(__name__)
# Allow cross-origin requests from the web page. This is important
# because the web page is a 'different origin' from the Flask server.
CORS(app)

# Create a directory to store uploaded audio files if it doesn't exist
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Define the API endpoint for uploading audio
@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    """
    Handles the audio file upload from the web client.
    """
    # Check if the request contains a file part
    if 'audio' not in request.files:
        return jsonify({'message': 'No audio file part in the request'}), 400

    audio_file = request.files['audio']

    # If the user does not select a file, the browser submits an
    # empty part without a filename.
    if audio_file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if audio_file:
        # Save the uploaded file with a safe filename
        # You could also generate a unique filename here
        filename = audio_file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        audio_file.save(file_path)

        print(f"File saved successfully at: {file_path}")
        return jsonify({'message': 'Audio file received successfully!', 'filename': filename}), 200

# The main block to run the server
if __name__ == '__main__':
    # Set host to '0.0.0.0' to make the server accessible from
    # other devices on your local network (not just your own machine).
    # debug=True allows for automatic reloading on code changes.
    app.run(host='0.0.0.0', port=5000, debug=True)

