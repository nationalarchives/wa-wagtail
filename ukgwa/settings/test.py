from .base import *  # noqa
from .base import LOGGING, SILENCED_SYSTEM_CHECKS

# #############
# General

SECRET_KEY = "fake_secret_key_to_run_tests"  # pragma: allowlist secret

ALLOWED_HOSTS = [".localhost"]

SILENCED_SYSTEM_CHECKS += [
    # It doesn't matter that STATICFILES_DIRS don't exist in tests
    "staticfiles.W004",
]

# Don't redirect to HTTPS in tests or send the HSTS header
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

# Don't insist on having run birdbath
BIRDBATH_REQUIRED = False

# Quieten down the logging in tests
LOGGING["handlers"]["console"]["class"] = "logging.NullHandler"

# Use local memory caching instead of redis when testing locally
# to prevent caching shenanigans
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Wagtail
WAGTAILADMIN_BASE_URL = "http://testserver"

# Task queue configuration to ensure tasks run immediately in the test environment
# https://docs.wagtail.org/en/stable/releases/6.4.html#background-tasks-run-at-end-of-current-transaction
TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.immediate.ImmediateBackend",
        "ENQUEUE_ON_COMMIT": False,
    }
}

# #############
# Performance

# By default, Django uses a computationally difficult algorithm for passwords hashing.
# We don't need such a strong algorithm in tests, so use MD5
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
