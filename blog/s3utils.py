from storages.backends.s3boto import S3BotoStorage

import paths


StaticS3BotoStorage = lambda: S3BotoStorage(location=paths.STATIC_ROOT)
MediaS3BotoStorage = lambda: S3BotoStorage(location=paths.MEDIA_DIR)