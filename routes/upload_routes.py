from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from typing import Tuple
from services.image_service import add_uploaded_image, is_duplicate_image, add_tags_to_image

upload_bp = Blueprint('upload', __name__)

def allowed_file(filename: str) -> bool:
    """
    Check if the file extension is allowed.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@upload_bp.route('/api/upload', methods=['POST'])
def upload_image() -> Tuple[jsonify, int]:
    """
    Handle image upload requests.

    Returns:
        Tuple[jsonify, int]: A JSON response and HTTP status code.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)
            
            # Save the file temporarily to check for duplicates
            file.save(file_path)
            
            if is_duplicate_image(file_path):
                os.remove(file_path)  # Remove the temporary file
                return jsonify({'error': 'Duplicate image. This image has already been uploaded.'}), 400
            
            tags = request.form.get('tags', '').split(',')
            tags = [tag.strip() for tag in tags if tag.strip()]
            new_image = add_uploaded_image(filename, file_path, tags)
            return jsonify(new_image), 201
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)  # Remove the temporary file if it exists
            return jsonify({'error': f'An error occurred while processing the image: {str(e)}'}), 500
    return jsonify({'error': 'Invalid file type'}), 400

@upload_bp.route('/api/add_tags', methods=['POST'])
def add_tags() -> Tuple[jsonify, int]:
    """
    Add tags to an existing image.

    Returns:
        Tuple[jsonify, int]: A JSON response and HTTP status code.
    """
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
