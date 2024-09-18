from flask import Flask, render_template, jsonify, request
from mock_data import MOCK_GIFS
import random

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/search")
def search_gifs():
    query = request.args.get("q", "")
    # In a real application, we would call the Giphy API here
    # For this mock version, we'll return random GIFs from our mock data
    results = random.sample(MOCK_GIFS, min(len(MOCK_GIFS), 20))
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
