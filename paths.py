import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(__file__)

APP_DIR = os.path.join(BASE_DIR, "app")
TEMPLATE_DIR = os.path.join(BASE_DIR, "template")

VENDOR_DIR = os.path.join(BASE_DIR, "vendor")
VENDOR_SWAGGER_DIR = os.path.join(VENDOR_DIR, "django-rest-swagger")

# add all user application paths to the project
sys.path.insert(0, APP_DIR)
sys.path.insert(0, VENDOR_DIR)
sys.path.insert(0, VENDOR_SWAGGER_DIR)