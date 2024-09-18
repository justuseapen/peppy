import random

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

def add_uploaded_image(title, image_url, tags):
    new_id = str(len(MOCK_IMAGES) + 1)
    new_image = {
        "id": new_id,
        "title": title,
        "tags": tags,
        "images": {
            "fixed_height": {
                "url": image_url
            },
            "original": {
                "url": image_url
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
