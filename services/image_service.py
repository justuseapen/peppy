from typing import List, Dict, Optional
import random
import imagehash
from PIL import Image
import logging

logging.basicConfig(level=logging.DEBUG)

MOCK_IMAGES: List[Dict[str, any]] = [
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
    # ... (other mock images)
]

IMAGE_HASHES: List[Optional[imagehash.ImageHash]] = []

def calculate_gif_hash(file_path: str) -> Optional[imagehash.ImageHash]:
    """
    Calculate the hash of the first frame of a GIF image.

    Args:
        file_path (str): The path to the GIF file.

    Returns:
        Optional[imagehash.ImageHash]: The hash of the first frame, or None if an error occurs.
    """
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

def add_uploaded_image(title: str, file_path: str, tags: List[str]) -> Dict[str, any]:
    """
    Add a new uploaded image to the MOCK_IMAGES list.

    Args:
        title (str): The title of the uploaded image.
        file_path (str): The path to the uploaded image file.
        tags (List[str]): A list of tags associated with the image.

    Returns:
        Dict[str, any]: The newly created image object.
    """
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

def add_tags_to_image(image_id: str, new_tags: List[str]) -> Optional[Dict[str, any]]:
    """
    Add new tags to an existing image.

    Args:
        image_id (str): The ID of the image to update.
        new_tags (List[str]): A list of new tags to add to the image.

    Returns:
        Optional[Dict[str, any]]: The updated image object, or None if the image is not found.
    """
    for image in MOCK_IMAGES:
        if image["id"] == image_id:
            image["tags"] = list(set(image["tags"] + new_tags))
            return image
    return None

def is_duplicate_image(file_path: str) -> bool:
    """
    Check if an uploaded image is a duplicate of an existing image.

    Args:
        file_path (str): The path to the uploaded image file.

    Returns:
        bool: True if the image is a duplicate, False otherwise.
    """
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
