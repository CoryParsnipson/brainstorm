from storages.backends.s3boto import S3BotoStorage

import paths
from slackerparadise.settings.production import STATIC_ROOT


StaticS3BotoStorage = lambda: S3BotoStorage(location=STATIC_ROOT)
MediaS3BotoStorage = lambda: S3BotoStorage(location=paths.MEDIA_DIR)