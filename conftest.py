import pytest
import sys
from django.conf import settings

def pytest_configure():
    settings.TESTING = True

    settings.STORAGES['staticfiles']['BACKEND'] = (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )

    if "whitenoise" in settings.INSTALLED_APPS:
        from whitenoise.storage import CompressedManifestStaticFilesStorage
        settings.STORAGES["staticfiles"]["BACKEND"] = CompressedManifestStaticFilesStorage