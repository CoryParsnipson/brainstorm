import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

KEYRING_DIR = os.path.join(BASE_DIR)
DATABASE_DIR = os.path.join(BASE_DIR, "database")

TEMPLATE_DIR = os.path.join(BASE_DIR, "template")

STATIC_ROOT = "static"

STATIC_DIR = os.path.join(BASE_DIR, "static")
IMAGE_DIR = os.path.join(STATIC_DIR, "images")

MEDIA_DIR = "media"
MEDIA_IMAGE_DIR = "images"
MEDIA_VIDEO_DIR = "videos"
MEDIA_FILE_DIR = "files"

MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_DIR)
MEDIA_IMAGE_ROOT = os.path.join(BASE_DIR, MEDIA_DIR, MEDIA_IMAGE_DIR)
MEDIA_VIDEO_ROOT = os.path.join(BASE_DIR, MEDIA_DIR, MEDIA_VIDEO_DIR)
MEDIA_FILE_ROOT = os.path.join(BASE_DIR, MEDIA_DIR, MEDIA_FILE_DIR)