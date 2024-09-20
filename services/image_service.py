from typing import List, Dict, Optional
import random
import string
import imagehash
from PIL import Image
import logging
import io
from replit import db

logging.basicConfig(level=logging.DEBUG)

MOCK_IMAGES = [
    {
        "id": "1",
        "title": "Happy Cat",
        "tags": ["cat", "happy", "cute"],
        "images": {
            "fixed_height": {
                "url": "https://media.giphy.com/media/ICOgUNjpvO0PC/200.gif"
            },
            "original": {
                "url": "https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif"
            }
        }
    },
    # Add more mock images here...
]

IMAGE_HASHES = []

def calculate_gif_hash(file_path: str) -> Optional[imagehash.ImageHash]:
    try:
        image_data = db.get(file_path)
        if image_data is None:
            logging.warning(f"Image data not found for {file_path}")
            return None
        with Image.open(io.BytesIO(image_data)) as img:
            frames = []
            try:
                while True:
                    frames.append(imagehash.average_hash(img.convert('RGB')))
                    img.seek(img.tell() + 1)
            except EOFError:
                pass
        if frames:
            return frames[0]  # Return the hash of the first frame
        else:
            logging.warning(f"No frames found in {file_path}")
            return None
    except Exception as e:
        logging.error(f"Error calculating GIF hash for {file_path}: {str(e)}")
        return None

def add_uploaded_image(title: str, file_path: str, tags: List[str]) -> Dict:
    new_id = str(len(MOCK_IMAGES) + 1)
    new_hash = calculate_gif_hash(file_path)
    if new_hash is not None:
        IMAGE_HASHES.append(new_hash)
        logging.debug(f"Added new hash to IMAGE_HASHES: {new_hash}")
    else:
        logging.warning(f"Failed to calculate hash for {file_path}")
    new_image = {
        "id": new_id,
        "title": title,
        "tags": tags,
        "images": {
            "fixed_height": {
                "url": file_path
            },
            "original": {
                "url": file_path
            }
        }
    }
    MOCK_IMAGES.append(new_image)
    return new_image

def add_tags_to_image(image_id: str, new_tags: List[str]) -> Optional[Dict]:
    for image in MOCK_IMAGES:
        if image["id"] == image_id:
            image["tags"] = list(set(image["tags"] + new_tags))
            return image
    return None

def is_duplicate_image(file_path: str) -> bool:
    try:
        new_hash = calculate_gif_hash(file_path)
        if new_hash is None:
            return False
        logging.debug(f"Checking for duplicate: {file_path}, hash: {new_hash}")
        for idx, existing_hash in enumerate(IMAGE_HASHES):
            if existing_hash is not None:
                difference = abs(new_hash - existing_hash)
                logging.debug(f"Comparing with IMAGE_HASHES[{idx}]: {existing_hash}, difference: {difference}")
                if difference <= 5:
                    logging.debug(f"Duplicate found: {file_path}")
                    return True
        logging.debug(f"No duplicate found: {file_path}")
        return False
    except Exception as e:
        logging.error(f"Error checking for duplicate image: {str(e)}")
        return False

# Initialize IMAGE_HASHES with hashes of MOCK_IMAGES
for image in MOCK_IMAGES:
    url = image["images"]["original"]["url"]
    hash_value = calculate_gif_hash(url)
    if hash_value:
        IMAGE_HASHES.append(hash_value)
        logging.debug(f"Added hash for {url} to IMAGE_HASHES: {hash_value}")
    else:
        logging.warning(f"Failed to calculate hash for {url}")

logging.debug(f"Initialized IMAGE_HASHES: {IMAGE_HASHES}")
