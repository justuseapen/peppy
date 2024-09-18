import random
import imagehash
from PIL import Image
import logging

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
    {
        "id": "2",
        "title": "Excited Dog",
        "tags": ["dog", "excited", "funny"],
        "images": {
            "fixed_height": {
                "url": "https://media.giphy.com/media/l0MYGb1LuF3fyP8NW/200.gif"
            },
            "original": {
                "url": "https://media.giphy.com/media/l0MYGb1LuF3fyP8NW/giphy.gif"
            }
        }
    },
    {
        "id": "3",
        "title": "Funny Monkey",
        "tags": ["monkey", "funny", "animal"],
        "images": {
            "fixed_height": {
                "url": "https://media.giphy.com/media/8YBm95B5JNIXTWp5on/200.gif"
            },
            "original": {
                "url": "https://media.giphy.com/media/8YBm95B5JNIXTWp5on/giphy.gif"
            }
        }
    },
    {
        "id": "4",
        "title": "Dancing Baby",
        "tags": ["baby", "dancing", "cute"],
        "images": {
            "fixed_height": {
                "url": "https://media.giphy.com/media/l0HlGmv4WqldO9c5y/200.gif"
            },
            "original": {
                "url": "https://media.giphy.com/media/l0HlGmv4WqldO9c5y/giphy.gif"
            }
        }
    },
    {
        "id": "5",
        "title": "Surprised Pikachu",
        "tags": ["pikachu", "surprised", "meme"],
        "images": {
            "fixed_height": {
                "url": "https://media.giphy.com/media/6nWhy3ulBL7GSCvKw6/200.gif"
            },
            "original": {
                "url": "https://media.giphy.com/media/6nWhy3ulBL7GSCvKw6/giphy.gif"
            }
        }
    }
]

IMAGE_HASHES = []

def calculate_gif_hash(file_path):
    try:
        with Image.open(file_path) as img:
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

def add_uploaded_image(title, file_path, tags):
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

def add_tags_to_image(image_id, new_tags):
    for image in MOCK_IMAGES:
        if image["id"] == image_id:
            image["tags"] = list(set(image["tags"] + new_tags))
            return image
    return None

def is_duplicate_image(file_path):
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
