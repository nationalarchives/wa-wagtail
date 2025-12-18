from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock as WagtailEmbedBlock
from wagtail.embeds.embeds import get_embed
from wagtail.embeds.exceptions import EmbedException
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from ..constants import GROUP_CALLOUTS, GROUP_MEDIA, GROUP_TEXT


class RichTextBlock(blocks.RichTextBlock):
    class Meta:
        template = "components/streamfield/richtext.html"


class InternalLinkBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock()
    link_text = blocks.CharBlock(required=False)

    class Meta:
        label = "Internal link"
        icon = "link"


class ExternalLinkBlock(blocks.StructBlock):
    url = blocks.URLBlock(label="URL")
    link_text = blocks.CharBlock()

    class Meta:
        label = "External link"
        icon = "link"


class LinkBlock(blocks.StreamBlock):
    internal_link = InternalLinkBlock()
    external_link = ExternalLinkBlock()

    class Meta:
        label = "Link"
        icon = "link"
        group = GROUP_TEXT
        max_num = 1


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.CharBlock(required=False)
    alt_text = blocks.CharBlock(
        required=False,
        help_text="By default the image title (shown above) is used as the alt text. "
        "Use this field to provide more specific alt text if required.",
    )
    image_is_decorative = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="If checked, this will make the alt text empty.",
    )

    class Meta:
        label = "Image"
        icon = "image"
        group = GROUP_MEDIA
        template = "components/streamfield/image_block.html"

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        ctx["image"] = value["image"]
        if ctx["image"] is None:
            # The template will not render anything if the image is None
            return ctx

        ctx["caption"] = value["caption"]
        ctx["alt_text"] = value["alt_text"]
        ctx["image_is_decorative"] = value["image_is_decorative"]

        # If the image is decorative, we don't need alt text
        if value.get("image_is_decorative"):
            ctx["image_alt_text"] = ""
        elif custom_alt_text := value.get("alt_text"):
            ctx["image_alt_text"] = custom_alt_text
        else:
            ctx["image_alt_text"] = value["image"].title

        return ctx


class QuoteBlock(blocks.StructBlock):
    quote = blocks.CharBlock(form_classname="title")
    attribution = blocks.CharBlock(required=False)
    link = LinkBlock(required=False)

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        ctx["quote"] = value["quote"]
        ctx["attribution"] = value["attribution"]

        if value["link"]:
            link_value = value["link"][0].value
            if "page" in link_value and link_value["page"]:
                page = link_value["page"]
                ctx["link_url"] = page.url
                ctx["link_text"] = link_value.get("link_text") or page.title
            elif "url" in link_value and link_value["url"]:
                ctx["link_url"] = link_value["url"]
                ctx["link_text"] = link_value.get("link_text")
        return ctx

    class Meta:
        label = "Quote"
        icon = "openquote"
        group = GROUP_TEXT
        template = "components/streamfield/quote_block.html"


class AccordionSectionBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=200)
    content = blocks.CharBlock()

    class Meta:
        label = "Sections"
        icon = "title"


class AccordionBlock(blocks.StructBlock):
    sections = blocks.ListBlock(
        AccordionSectionBlock(),
    )

    class Meta:
        label = "Accordion"
        icon = "list-ol"
        group = GROUP_TEXT
        template = "components/streamfield/accordion_block.html"

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        ctx["accordions"] = value["sections"]
        return ctx


class EmbedBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    description = blocks.TextBlock(required=False)
    embed = WagtailEmbedBlock()

    class Meta:
        icon = "link"
        template = "components/streamfield/video_embed_block.html"

    def get_embed_instance(self, value):
        embed = value["embed"]
        if embed is None:
            return None

        try:
            return get_embed(embed.url)
        except EmbedException:
            return None

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        if embed := self.get_embed_instance(value):
            context["thumbnail_url"] = embed.thumbnail_url
            context["is_youtube"] = embed.provider_name.lower() == "youtube"

        return context


class StatSectionBlock(blocks.StructBlock):
    number = blocks.CharBlock(
        required=False,
        help_text="Enter the statistic number. This will be displayed in a large font size.",
    )
    sentence = blocks.CharBlock(
        required=False,
        max_length=100,
        help_text="Enter a short sentence describing the statistic. This will be displayed in a smaller font size.",
    )
    text = blocks.CharBlock(required=False)
    link = LinkBlock(required=False)

    class Meta:
        label = "Stat"
        icon = "list-ul"


class StatBlock(blocks.StructBlock):
    stats = blocks.ListBlock(StatSectionBlock(), min_num=1, max_num=3)

    class Meta:
        label = "Stats"
        icon = "pick"
        group = GROUP_TEXT
        template = "components/streamfield/stat_block.html"

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context)

        ctx["stats"] = []
        for stat in value["stats"]:
            stat_context = {
                "number": stat.get("number"),
                "text": stat.get("text"),
                "sentence": stat.get("sentence"),
            }

            if stat.get("link"):
                for link_block in stat["link"]:
                    if link_block.block_type == "internal_link":
                        page = link_block.value.get("page")
                        if page:
                            stat_context["link_url"] = page.url
                            stat_context["link_text"] = (
                                link_block.value.get("link_text") or page.title
                            )
                    elif link_block.block_type == "external_link":
                        stat_context["link_url"] = link_block.value.get("url")
                        stat_context["link_text"] = link_block.value.get("link_text")

            ctx["stats"].append(stat_context)
        return ctx


class StoryBlock(blocks.StreamBlock):
    """
    Main StreamField block to be inherited by Pages
    """

    heading = blocks.CharBlock(
        form_classname="title",
        label="Heading",
        icon="title",
        group=GROUP_TEXT,
        template="components/streamfield/heading_block.html",
    )
    paragraph = RichTextBlock(
        label="Rich text",
        group=GROUP_TEXT,
    )
    image = ImageBlock()
    quote = QuoteBlock()
    embed = EmbedBlock(
        label="Embed",
        group=GROUP_MEDIA,
    )
    call_to_action = SnippetChooserBlock(
        "core.CallToActionSnippet",
        label="Call To Action",
        group=GROUP_CALLOUTS,
        template="components/streamfield/call_to_action_block.html",
    )

    class Meta:
        template = "components/streamfield/stream_block.html"


class TableBlock(blocks.StaticBlock):
    """Deprecated: Stub for migration compatibility only"""

    class Meta:
        admin_text = "Deprecated table block"
