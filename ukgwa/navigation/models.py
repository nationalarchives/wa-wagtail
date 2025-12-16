from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField

from ukgwa.core.blocks import ImageBlock


class LinkBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock()
    title = blocks.CharBlock(
        help_text="Leave blank to use the page's own title", required=False
    )

    class Meta:
        template = ("components/navigation/menu_item.html",)


class LinkColumnWithHeaderBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        required=False, help_text="Leave blank if no header required."
    )
    links = blocks.ListBlock(LinkBlock())

    class Meta:
        template = ("components/navigation/footer_column.html",)


class LogoLinkBlock(blocks.StructBlock):
    logo = ImageBlock()
    url = blocks.URLBlock(required=False)

    class Meta:
        template = ("components/navigation/footer_logo_item.html",)


@register_setting(icon="list-ul")
class NavigationSettings(BaseSiteSetting, ClusterableModel):
    primary_navigation = StreamField(
        [("link", LinkBlock())],
        blank=True,
        help_text="Main site navigation",
    )
    secondary_navigation = StreamField(
        [("link", LinkBlock())],
        blank=True,
        help_text="Alternative navigation",
    )
    footer_navigation = StreamField(
        [("column", LinkColumnWithHeaderBlock())],
        blank=True,
        help_text="Multiple columns of footer links with optional header.",
    )
    footer_links = StreamField(
        [("link", LinkBlock())],
        blank=True,
        help_text="Single list of elements at the base of the page.",
    )
    footer_logo_cloud = StreamField(
        [("logo", LogoLinkBlock())],
        blank=True,
        help_text="Logo cloud at the base of the page.",
    )

    panels = [
        FieldPanel("primary_navigation"),
        FieldPanel("secondary_navigation"),
        FieldPanel("footer_navigation"),
        FieldPanel("footer_links"),
        FieldPanel("footer_logo_cloud"),
    ]
