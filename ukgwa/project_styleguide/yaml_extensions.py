import random
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile

from wagtail.models import Collection

from ukgwa.images.models import CustomImage

PATTERN_LIBRARY_COLLECTION = "pattern_library"
TEST_IMAGE_DIR = Path(settings.PROJECT_DIR) / "project_styleguide" / "tests" / "assets"


def _init_test_images(collection):
    """
    Load the test images into the database, adding them to the given collection.
    """
    images = [
        CustomImage(
            title=f"Test image {filepath.name}",
            description=filepath.stem.title(),
            file=ContentFile(filepath.read_bytes(), name=filepath.name),
            collection=collection,
        )
        for filepath in TEST_IMAGE_DIR.glob("*.webp")
    ]
    CustomImage.objects.bulk_create(images)


def get_random_image():
    """
    Return a random CustomImage instance for use in templates.
    Images are taken from the pattern library collection which will be
    automatically created if it doesn't exist(and populated with test images).
    """
    # Ideally we'd use Collection.objects.get_or_create() but that does not
    # work with MP_Node models (like Collection).
    try:
        collection = Collection.objects.get(name=PATTERN_LIBRARY_COLLECTION)
    except Collection.DoesNotExist:
        root = Collection.get_first_root_node()
        collection = root.add_child(name=PATTERN_LIBRARY_COLLECTION)
        _init_test_images(collection)

    images = CustomImage.objects.filter(collection=collection)

    return random.choice(images)


def get_test_rendition(rendition_filter):
    """
    Return a rendition from a random test image using the given rendition filter.

    Args:
        rendition_filter: A Wagtail image rendition filter string (e.g., "fill-500x400")
    """
    image = get_random_image()
    return image.get_rendition(rendition_filter)
