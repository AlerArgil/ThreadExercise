from django.core.files.storage import default_storage
from rest_framework import serializers


class FileExists:
    """
    Validator for check existing file
    """
    def __call__(self, value):
        if not default_storage.exists(value):
            message = 'File with name %s doesnt exists.' % value
            raise serializers.ValidationError(message)
