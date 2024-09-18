from flask import Flask, render_template
from routes.search_routes import search_bp
from routes.upload_routes import upload_bp
from routes.category_routes import category_bp, CATEGORIES
from config import Config
import logging

app = Flask(__name__)
app.config.from_object(Config)

logging.basicConfig(level=logging.DEBUG)

# Register blueprints
app.register_blueprint(search_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(category_bp)

@app.route("/")
def index():
    """
    Render the main page of the application.

    Returns:
        str: The rendered HTML template.
    """
    return render_template("index.html", categories=CATEGORIES)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config['DEBUG'])
