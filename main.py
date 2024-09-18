from flask import Flask, render_template, jsonify, request
from mock_data import MOCK_GIFS
import random

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
