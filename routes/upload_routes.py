from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import uuid
import io
from typing import Tuple, List, Dict
from services.image_service import add_uploaded_image, is_duplicate_image, add_tags_to_image
from replit import db

upload_bp = Blueprint('upload', __name__)

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@upload_bp.route('/api/upload', methods=['POST'])
def upload_image() -> Tuple[jsonify, int]:
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Upload to Replit's database
            db[unique_filename] = file.read()
            file_url = f"/api/image/{unique_filename}"
            
            if is_duplicate_image(file_url):
                return jsonify({'error': 'Duplicate image. This image has already been uploaded.'}), 400
            
            tags = request.form.get('tags', '').split(',')
            tags = [tag.strip() for tag in tags if tag.strip()]
            new_image = add_uploaded_image(filename, file_url, tags)
            return jsonify(new_image), 201
        except Exception as e:
            return jsonify({'error': f'An error occurred while processing the image: {str(e)}'}), 500
    return jsonify({'error': 'Invalid file type'}), 400

@upload_bp.route('/api/image/<filename>')
def serve_image(filename):
    try:
        image_data = db[filename]
        return send_file(io.BytesIO(image_data), mimetype='image/gif')
    except Exception as e:
        return jsonify({'error': f'Error retrieving image: {str(e)}'}), 404

@upload_bp.route('/api/add_tags', methods=['POST'])
def add_tags() -> Tuple[jsonify, int]:
    data = request.json
    image_id = data.get('image_id')
    new_tags = data.get('tags', [])
    
    if not image_id or not new_tags:
        return jsonify({'error': 'Image ID and tags are required'}), 400

    updated_image = add_tags_to_image(image_id, new_tags)
    if updated_image:
        return jsonify(updated_image), 200
    else:
        return jsonify({'error': 'Image not found'}), 404
