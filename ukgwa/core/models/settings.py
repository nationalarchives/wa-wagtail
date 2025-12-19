from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField

from bs4 import BeautifulSoup

from ukgwa.images.models import CustomImage

__all__ = [
    "SocialMediaSettings",
    "SystemMessagesSettings",
    "Tracking",
]


@register_setting
class SocialMediaSettings(BaseSiteSetting):
    twitter_handle = models.CharField(
        max_length=255,
        blank=True,
        help_text="Your Twitter username without the @, e.g. katyperry",
    )
    facebook_app_id = models.CharField(
        max_length=255, blank=True, help_text="Your Facebook app ID."
    )
    instagram_username = models.CharField(
        max_length=255,
        blank=True,
        help_text="Your Instagram username without the @, e.g. katyperry",
    )
    linkedin_company_id = models.CharField(
        max_length=255, blank=True, help_text="Your LinkedIn company ID."
    )
    default_sharing_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Default sharing text to use if social text has not been set on a page.",
    )
    default_sharing_image = models.ForeignKey(
        CustomImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Default sharing image to use if social image has not been set on a page.",
    )
    site_name = models.CharField(
        max_length=255,
        blank=True,
        default="UK Government Web Archive",
        help_text="Site name, used by Open Graph.",
    )


@register_setting
class SystemMessagesSettings(BaseSiteSetting):
    class Meta:
        verbose_name = "system messages"

    title_404 = models.CharField("Title", max_length=255, default="Page not found")
    body_404 = RichTextField(
        "Text",
        default="<p>You may be trying to find a page that doesn&rsquo;t exist or has been moved.</p>",
    )

    title_alert = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional title, displayed next to the alert icon.",
    )
    description_alert = RichTextField(features=["link"], null=True, blank=False)
    active_alert = models.BooleanField(
        default=False,
        help_text=(
            "Check this field to show the alert banner, "
            "uncheck it to hide the alert banner."
        ),
    )

    panels = [
        MultiFieldPanel([FieldPanel("title_404"), FieldPanel("body_404")], "404 page"),
        MultiFieldPanel(
            [
                FieldPanel("title_alert"),
                FieldPanel("description_alert"),
                FieldPanel("active_alert"),
            ],
            "Alert Banner",
        ),
    ]

    def clean(self):
        if self.description_alert:
            soup = BeautifulSoup(self.description_alert, "html.parser")
            # Remove all elements that might cause new lines
            for block_tag in ["p", "br"]:
                for tag in soup.find_all(block_tag):
                    tag.unwrap()  # This removes the tag but keeps its content
            self.description_alert = str(soup)
        return super().clean()


@register_setting(icon="view")
class Tracking(BaseSiteSetting):
    google_tag_manager_id = models.CharField(
        max_length=255,
        blank="True",
        help_text="Your Google Tag Manager ID",
    )
