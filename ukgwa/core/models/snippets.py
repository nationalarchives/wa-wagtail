from django.db import models

from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.snippets.models import register_snippet

__all__ = [
    "CallToActionSnippet",
]


@register_snippet
class CallToActionSnippet(models.Model):
    title = models.CharField(max_length=255)
    summary = RichTextField(blank=True, max_length=255)
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    image_alt_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Alt text for the image, if left blank the image will be set as decorative.",
    )
    image_is_decorative = models.BooleanField(
        default=False,
        help_text="If checked, this will make the alt text empty.",
    )

    link = StreamField(
        blocks.StreamBlock(
            [
                (
                    "external_link",
                    blocks.StructBlock(
                        [("url", blocks.URLBlock()), ("title", blocks.CharBlock())],
                        icon="link",
                    ),
                ),
                (
                    "internal_link",
                    blocks.StructBlock(
                        [
                            ("page", blocks.PageChooserBlock()),
                            ("title", blocks.CharBlock(required=False)),
                        ],
                        icon="link",
                    ),
                ),
            ],
            max_num=1,
        ),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("summary"),
        FieldPanel("image"),
        FieldPanel("image_alt_text"),
        FieldPanel("image_is_decorative"),
        FieldPanel("link"),
    ]

    def get_image_alt_text(self):
        if self.image_is_decorative:
            return ""

        if self.image_alt_text:
            return self.image_alt_text

        if self.image is not None:
            return self.image.title

        return ""

    def get_link_text(self):
        # Link is required, so we should always have
        # an element with index 0
        block = self.link[0]

        title = block.value["title"]
        if block.block_type == "external_link":
            return title

        # Title is optional for internal_link
        # so fallback to page's title, if it's empty
        return title or block.value["page"].title

    def get_link_url(self):
        # Link is required, so we should always have
        # an element with index 0
        block = self.link[0]

        if block.block_type == "external_link":
            return block.value["url"]

        return block.value["page"].get_url()

    def __str__(self):
        return self.title
