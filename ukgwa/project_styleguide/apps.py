from django.apps import AppConfig

import yaml


class ProjectStyleguideConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "ukgwa.project_styleguide"

    def ready(self):
        # Register a custom !testimage and !testrendition yaml tags for use in the pattern library
        from .yaml_extensions import get_random_image, get_test_rendition

        yaml.add_constructor("!testimage", lambda loader, node: get_random_image())
        yaml.add_constructor(
            "!testrendition",
            lambda loader, node: get_test_rendition(loader.construct_scalar(node)),
        )
