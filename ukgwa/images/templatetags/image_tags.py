from django import template

register = template.Library()


@register.inclusion_tag("components/responsive_image/responsive_image.html")
def responsive_image(
    image,
    rendition_1x,
    rendition_2x,
    class_name=None,
    img_class=None,
    alt_text=None,
    lazy_loading=True,
    # Determines whether the object-cover property is applied to the image.
    # If it is not, the object-position inline style is not used.
    object_cover=True,
):
    # Get renditions based on the provided filter specs
    rendition_1x = image.get_rendition(rendition_1x)
    rendition_2x = image.get_rendition(rendition_2x)

    # Generate webp versions of the renditions
    rendition_1x_webp = image.get_rendition(rendition_1x.filter_spec + "|format-webp")
    rendition_2x_webp = image.get_rendition(rendition_2x.filter_spec + "|format-webp")

    alt_text = rendition_1x.alt if alt_text is None else alt_text

    return {
        "rendition_1x": rendition_1x,
        "rendition_2x": rendition_2x,
        "rendition_1x_webp": rendition_1x_webp,
        "rendition_2x_webp": rendition_2x_webp,
        "class_name": class_name if class_name else "",
        "img_class": img_class if img_class else "",
        "alt_text": alt_text,
        "lazy_loading": lazy_loading,
        "object_cover": object_cover,
    }
