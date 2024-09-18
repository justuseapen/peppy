from flask import Flask, render_template, jsonify, request, url_for
from mock_data import MOCK_GIFS, add_uploaded_gif
import random
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/search")
def search_gifs():
    query = request.args.get("q", "").lower()
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 20))

    # Filter GIFs based on the query (case-insensitive)
    filtered_gifs = [gif for gif in MOCK_GIFS if query in gif["title"].lower()]

    # Paginate the results
    paginated_gifs = filtered_gifs[offset:offset + limit]

    return jsonify(paginated_gifs)

@app.route('/api/upload', methods=['POST'])
def upload_gif():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.lower().endswith('.gif'):
        filename = secure_filename(file.filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        gif_url = url_for('static', filename=f'uploads/{filename}')
        new_gif = add_uploaded_gif(filename, gif_url)
        return jsonify(new_gif), 201
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
