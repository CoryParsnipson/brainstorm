import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(__file__)

DATABASE_DIR = os.path.join(BASE_DIR, "database")

TEMPLATE_DIR = os.path.join(BASE_DIR, "template")

STATIC_DIR = os.path.join(BASE_DIR, "static")
IMAGE_DIR = os.path.join(STATIC_DIR, "images")

MEDIA_ROOT = "media"
MEDIA_IMAGE_ROOT = os.path.join(MEDIA_ROOT, "images")
MEDIA_VIDEO_ROOT = os.path.join(MEDIA_ROOT, "videos")
MEDIA_FILE_ROOT = os.path.join(MEDIA_ROOT, "files")

MEDIA_DIR = os.path.join(BASE_DIR, MEDIA_ROOT)
MEDIA_IMAGE_DIR = os.path.join(BASE_DIR, MEDIA_IMAGE_ROOT)
MEDIA_VIDEO_DIR = os.path.join(BASE_DIR, MEDIA_VIDEO_ROOT)
MEDIA_FILE_DIR = os.path.join(BASE_DIR, MEDIA_FILE_ROOT)

VENDOR_DIR = os.path.join(BASE_DIR, "vendor")

# add all user application paths to the project
sys.path.insert(0, VENDOR_DIR)