from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField

from .blocks import ExternalLinkBlock


def get_default_link():
    """Return default structure for one empty link"""
    return [{"type": "link", "value": {"url": "", "link_text": ""}}]


class HighlightedLinksMixin(models.Model):
    """Reusable mixin for adding highlighted links section to any page"""

    highlighted_links_heading = models.CharField(
        max_length=255,
        default="",
        help_text="Heading for the highlighted links section",
    )
    highlighted_links = StreamField(
        [("link", ExternalLinkBlock())],
        min_num=3,
        max_num=3,
        default=get_default_link,
        use_json_field=True,
        help_text="Add between 1 and 3 external links",
    )

    class Meta:
        abstract = True

    @staticmethod
    def get_highlighted_links_panels():
        """Return the panel configuration for highlighted links"""
        return [
            FieldPanel("highlighted_links_heading"),
            FieldPanel("highlighted_links"),
        ]
