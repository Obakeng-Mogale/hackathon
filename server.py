# filename: server.py
import os
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for the frontend to access the API
CORS(app)

# Directory where audio files are stored
DATA_DIR = 'uploads'
# Create the uploads directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Route to serve the audio files directly
@app.route('/uploads/<path:filename>')
def get_file(filename):
    return send_from_directory(DATA_DIR, filename, as_attachment=False)

# Route to get the list of recordings
@app.route('/api/recordings')
def list_recordings():
    try:
        # List all files in the uploads directory
        files = os.listdir(DATA_DIR)
        recordings = []
        for filename in files:
            # Filter for .wav files and parse the filename for date
            if filename.endswith('.wav') and filename.startswith('recording-'):
                try:
                    # Extract timestamp from the filename
                    # Filename format: recording-YYYY-MM-DDTHH-MM-SS-sssZ.wav
                    timestamp_str = filename.replace('recording-', '').replace('.wav', '')
                    
                    # The timestamp now contains milliseconds and a timezone ('-sssZ').
                    # We need to parse this part: YYYY-MM-DDTHH-MM-SS
                    # The easiest way is to find the last hyphen, which precedes the milliseconds.
                    last_hyphen_index = timestamp_str.rfind('-')
                    if last_hyphen_index != -1:
                        timestamp_to_parse = timestamp_str[:last_hyphen_index]
                    else:
                        timestamp_to_parse = timestamp_str
                    
                    # Now we can parse the cleaned-up timestamp string
                    dt_object = datetime.strptime(timestamp_to_parse, '%Y-%m-%dT%H-%M-%S')
                    formatted_date = dt_object.strftime('%B %d, %Y - %I:%M %p')

                    # Create a dictionary for each recording
                    recordings.append({
                        'title': f"Recording - {formatted_date}",
                        'date': formatted_date,
                        'url': f'/uploads/{filename}'
                    })
                except ValueError as e:
                    print(f"Skipping file due to ValueError: {filename}, Error: {e}")
                    continue
        
        # Return the list of recordings as JSON
        # Sort by date, most recent first
        sorted_recordings = sorted(recordings, key=lambda r: datetime.strptime(r['date'], '%B %d, %Y - %I:%M %p'), reverse=True)
        return jsonify(sorted_recordings)

    except Exception as e:
        # Return an error message if something goes wrong
        return jsonify({'error': str(e)}), 500

# Route to handle audio file uploads
@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file part in the request'}), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        filename = file.filename
        file_path = os.path.join(DATA_DIR, filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    
    return jsonify({'error': 'Something went wrong'}), 500

if __name__ == '__main__':
    # Run the Flask app on localhost, port 5000
    app.run(debug=True, port=5000)
