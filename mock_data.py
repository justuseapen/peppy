import random

MOCK_IMAGES = [
    {
        "id": "1",
        "title": "Happy Cat",
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

def add_uploaded_image(title, image_url):
    new_id = str(len(MOCK_IMAGES) + 1)
    new_image = {
        "id": new_id,
        "title": title,
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
