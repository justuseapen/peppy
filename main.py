from flask import Flask, render_template, jsonify, request, url_for
from mock_data import MOCK_IMAGES, add_uploaded_image, add_tags_to_image
import random
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

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

    # Filter images based on the query (case-insensitive) and tags
    filtered_images = [
        image for image in MOCK_IMAGES
        if query in image["title"].lower() or
        any(query in tag.lower() for tag in image["tags"])
    ]

    # Paginate the results
    paginated_images = filtered_images[offset:offset + limit]

    return jsonify(paginated_images)

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        image_url = url_for('static', filename=f'uploads/{filename}')
        tags = request.form.get('tags', '').split(',')
        tags = [tag.strip() for tag in tags if tag.strip()]
        new_image = add_uploaded_image(filename, image_url, tags)
        return jsonify(new_image), 201
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
