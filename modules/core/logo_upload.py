"""
Logo Upload API Endpoint
Allows uploading logo files via the web interface
"""

from flask import request, jsonify
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg', 'heic'}
UPLOAD_FOLDER = 'static/images'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Add this route to app.py
"""
@app.route('/api/upload-logo', methods=['POST'])
def upload_logo():
    if 'logo' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['logo']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Convert to standard name
        ext = filename.rsplit('.', 1)[1].lower()
        if ext == 'heic':
            # Note: HEIC needs conversion - see conversion script
            new_filename = 'lariat-logo-white-original.heic'
        else:
            new_filename = f'lariat-logo-white.{ext}'

        filepath = os.path.join(UPLOAD_FOLDER, new_filename)
        file.save(filepath)

        return jsonify({
            'success': True,
            'message': 'Logo uploaded successfully',
            'filename': new_filename
        })

    return jsonify({'error': 'Invalid file type'}), 400
"""
