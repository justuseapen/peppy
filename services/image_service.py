from typing import List, Dict, Optional
import random
import string
import imagehash
from PIL import Image
import logging
import io
from replit.object_storage import Client

logging.basicConfig(level=logging.DEBUG)

client = Client()

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
]

IMAGE_HASHES: List[Optional[imagehash.ImageHash]] = []

def generate_mock_images(num_images: int) -> List[Dict[str, any]]:
    mock_images = []
    categories = ["Funny", "Reactions", "Animals", "Memes", "Sports", "TV & Movies"]
    for i in range(num_images):
        title = f"Mock Image {i+1}"
        tags = random.sample(categories, k=random.randint(1, 3))
        image_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        mock_images.append({
            "id": str(i+1),
            "title": title,
            "tags": tags,
            "images": {
                "fixed_height": {
                    "url": f"https://via.placeholder.com/200x200.gif?text={image_id}"
                },
                "original": {
                    "url": f"https://via.placeholder.com/500x500.gif?text={image_id}"
                }
            }
        })
    return mock_images

MOCK_IMAGES.extend(generate_mock_images(1000))

def calculate_gif_hash(file_url: str) -> Optional[imagehash.ImageHash]:
    try:
        filename = file_url.split('/')[-1]
        image_data = client.download_as_bytes(filename)
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
            logging.warning(f"No frames found in {file_url}")
            return None
    except Exception as e:
        logging.error(f"Error calculating GIF hash for {file_url}: {str(e)}")
        return None

def add_uploaded_image(title: str, file_url: str, tags: List[str]) -> Dict[str, any]:
    new_id = str(len(MOCK_IMAGES) + 1)
    new_hash = calculate_gif_hash(file_url)
    if new_hash is not None:
        IMAGE_HASHES.append(new_hash)
        logging.debug(f"Added new hash to IMAGE_HASHES: {new_hash}")
    else:
        logging.warning(f"Failed to calculate hash for {file_url}")
    new_image = {
        "id": new_id,
        "title": title,
        "tags": tags,
        "images": {
            "fixed_height": {
                "url": file_url
            },
            "original": {
                "url": file_url
            }
        }
    }
    MOCK_IMAGES.append(new_image)
    return new_image

def add_tags_to_image(image_id: str, new_tags: List[str]) -> Optional[Dict[str, any]]:
    for image in MOCK_IMAGES:
        if image["id"] == image_id:
            image["tags"] = list(set(image["tags"] + new_tags))
            return image
    return None

def is_duplicate_image(file_url: str) -> bool:
    try:
        new_hash = calculate_gif_hash(file_url)
        if new_hash is None:
            return False
        logging.debug(f"Checking for duplicate: {file_url}, hash: {new_hash}")
        for idx, existing_hash in enumerate(IMAGE_HASHES):
            if existing_hash is not None:
                difference = abs(new_hash - existing_hash)
                logging.debug(f"Comparing with IMAGE_HASHES[{idx}]: {existing_hash}, difference: {difference}")
                if difference <= 5:
                    logging.debug(f"Duplicate found: {file_url}")
                    return True
        logging.debug(f"No duplicate found: {file_url}")
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
