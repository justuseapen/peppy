from flask import Flask, render_template, jsonify, request, url_for
from mock_data import MOCK_IMAGES, add_uploaded_image, add_tags_to_image, is_duplicate_image
import random
import os
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/search")
def search_images():
    query = request.args.get("q", "").lower()
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 20))

    def calculate_relevance(image):
        score = 0
        if query == image["title"].lower():
            score += 3  # Exact title match
        elif query in image["title"].lower():
            score += 2  # Partial title match
        if query in image["tags"]:
            score += 1  # Tag match
        return score

    # Filter and score images based on the query (case-insensitive)
    filtered_images = [
        (image, calculate_relevance(image))
        for image in MOCK_IMAGES
        if query in image["title"].lower() or query in image["tags"]
    ]

    # Sort images by relevance score (descending order)
    sorted_images = sorted(filtered_images, key=lambda x: x[1], reverse=True)

    # Paginate the results
    paginated_images = [image for image, score in sorted_images[offset:offset + limit]]

    return jsonify(paginated_images)

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file temporarily to check for duplicates
            file.save(file_path)
            
            logging.debug(f"Checking for duplicate image: {file_path}")
            is_duplicate = is_duplicate_image(file_path)
            logging.debug(f"is_duplicate_image result: {is_duplicate}")
            
            if is_duplicate:
                os.remove(file_path)  # Remove the temporary file
                return jsonify({'error': 'Duplicate image. This image has already been uploaded.'}), 400
            
            tags = request.form.get('tags', '').split(',')
            tags = [tag.strip() for tag in tags if tag.strip()]
            new_image = add_uploaded_image(filename, file_path, tags)
            return jsonify(new_image), 201
        except Exception as e:
            logging.error(f"Error processing uploaded image: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)  # Remove the temporary file if it exists
            return jsonify({'error': f'An error occurred while processing the image: {str(e)}'}), 500
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/add_tags', methods=['POST'])
def add_tags():
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

@app.route('/api/trending')
def trending_gifs():
    limit = int(request.args.get("limit", 10))
    trending = random.sample(MOCK_IMAGES, min(limit, len(MOCK_IMAGES)))
    return jsonify(trending)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
