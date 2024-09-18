from flask import Blueprint, request, jsonify
from typing import List, Dict
from services.image_service import MOCK_IMAGES

category_bp = Blueprint('category', __name__)

CATEGORIES = ["Funny", "Reactions", "Animals", "Memes", "Sports", "TV & Movies"]

@category_bp.route('/api/categories')
def get_categories() -> jsonify:
    """
    Get the list of available categories.

    Returns:
        jsonify: A JSON response containing the list of categories.
    """
    return jsonify(CATEGORIES)

@category_bp.route('/api/category/<category>')
def category_gifs(category: str) -> jsonify:
    """
    Get a list of GIFs for a specific category.

    Args:
        category (str): The category to filter GIFs by.

    Returns:
        jsonify: A JSON response containing the filtered GIFs.
    """
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 20))
    
    filtered_images = [image for image in MOCK_IMAGES if category.lower() in [tag.lower() for tag in image["tags"]]]
    paginated_images = filtered_images[offset:offset + limit]
    
    return jsonify(paginated_images)
