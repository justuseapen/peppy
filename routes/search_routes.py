from flask import Blueprint, request, jsonify
from typing import List, Dict
from services.image_service import MOCK_IMAGES
import random

search_bp = Blueprint('search', __name__)

@search_bp.route("/api/search")
def search_images() -> jsonify:
    query = request.args.get("q", "").lower()
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 20))

    filtered_images = [
        image for image in MOCK_IMAGES
        if query in image["title"].lower() or any(query in tag.lower() for tag in image["tags"])
    ]

    total_results = len(filtered_images)
    paginated_images = filtered_images[offset:offset + limit]

    return jsonify({
        "images": paginated_images,
        "total_results": total_results,
        "has_more": offset + limit < total_results
    })

@search_bp.route('/api/trending')
def trending_gifs() -> jsonify:
    """
    Get a list of trending GIFs.

    Returns:
        jsonify: A JSON response containing the trending GIFs.
    """
    limit = int(request.args.get("limit", 10))
    shuffled_images = MOCK_IMAGES.copy()
    random.shuffle(shuffled_images)
    trending = shuffled_images[:limit]
    return jsonify(trending)

@search_bp.route("/api/untagged")
def untagged_images() -> jsonify:
    """
    Get a list of untagged images.

    Returns:
        jsonify: A JSON response containing the untagged images.
    """
    untagged = [image for image in MOCK_IMAGES if not image["tags"]]
    return jsonify(untagged)
