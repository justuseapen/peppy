from flask import Flask, render_template, jsonify, request, url_for
from mock_data import MOCK_IMAGES, add_uploaded_image
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

    # Filter images based on the query (case-insensitive)
    filtered_images = [image for image in MOCK_IMAGES if query in image["title"].lower()]

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
        new_image = add_uploaded_image(filename, image_url)
        return jsonify(new_image), 201
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
