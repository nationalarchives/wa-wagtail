import uuid

from django import template

from ukgwa.core.models import SocialMediaSettings

register = template.Library()


# Social text
@register.filter(name="social_text")
def social_text(page, site):
    return (
        getattr(page, "social_text", None)
        or SocialMediaSettings.for_site(site).default_sharing_text
    )


# Social image
@register.filter(name="social_image")
def social_image(page, site):
    return (
        getattr(page, "social_image", None)
        or SocialMediaSettings.for_site(site).default_sharing_image
    )


# Generate a unique ID
@register.simple_tag(name="unique_id")
def unique_id(prefix="uuid"):
    """
    Generate a unique ID string by appending a UUID to a prefix string
    Usage: {% unique_id "repeated-component-id" as new_unique_id %}
    """
    return f"{prefix}-{uuid.uuid4().hex[:16]}"
