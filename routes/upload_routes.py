from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import uuid
import io
import traceback
from typing import Tuple, List, Dict
from services.image_service import add_uploaded_image, is_duplicate_image, add_tags_to_image
from replit import db

upload_bp = Blueprint('upload', __name__)

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@upload_bp.route('/api/upload', methods=['POST'])
def upload_image() -> Tuple[jsonify, int]:
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Upload to Replit's database
            file_data = file.read()
            db[unique_filename] = file_data
            file_url = f"/api/image/{unique_filename}"
            
            current_app.logger.debug(f"File uploaded: {unique_filename}")
            current_app.logger.debug(f"File size: {len(file_data)} bytes")
            
            if is_duplicate_image(file_url):
                current_app.logger.warning(f"Duplicate image detected: {file_url}")
                return jsonify({'error': 'Duplicate image. This image has already been uploaded.'}), 400
            
            tags = request.form.get('tags', '').split(',')
            tags = [tag.strip() for tag in tags if tag.strip()]
            new_image = add_uploaded_image(filename, file_url, tags)
            current_app.logger.info(f"New image added: {new_image}")
            return jsonify(new_image), 201
        return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        current_app.logger.error(f"Error in upload_image: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': f'An error occurred while processing the image: {str(e)}'}), 500

@upload_bp.route('/api/image/<filename>')
def serve_image(filename):
    try:
        image_data = db[filename]
        return send_file(io.BytesIO(image_data), mimetype='image/gif')
    except Exception as e:
        current_app.logger.error(f"Error retrieving image {filename}: {str(e)}")
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
