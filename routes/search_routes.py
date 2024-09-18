from flask import Blueprint, request, jsonify
from typing import List, Dict
from services.image_service import MOCK_IMAGES
import random

search_bp = Blueprint('search', __name__)

@search_bp.route("/api/search")
def search_images() -> jsonify:
    """
    Search for images based on a query string.

    Returns:
        jsonify: A JSON response containing the search results.
    """
    query = request.args.get("q", "").lower()
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 20))

    def calculate_relevance(image: Dict[str, any]) -> int:
        """
        Calculate the relevance score of an image based on the search query.

        Args:
            image (Dict[str, any]): The image object to calculate relevance for.

        Returns:
            int: The relevance score of the image.
        """
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
