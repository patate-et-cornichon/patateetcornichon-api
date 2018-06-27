from storages.backends.s3boto3 import S3Boto3Storage


class MediaRootS3BotoStorage(S3Boto3Storage):
    location = 'media'


class StaticRootS3BotoStorage(S3Boto3Storage):
    location = 'static'
