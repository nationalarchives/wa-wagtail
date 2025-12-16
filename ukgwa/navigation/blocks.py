from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList

from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockValidationError

from ukgwa.core.blocks import ImageBlock


class LinkBlockStructValue(blocks.StructValue):
    def url(self):
        if page := self.get("page"):
            return page.url

        if external_link := self.get("external_link"):
            return external_link

        return ""

    def text(self):
        if self.get("page") and not self.get("title"):
            return self.get("page").title
        if title := self.get("title"):
            return title
        return ""

    def is_page(self):
        return bool(self.get("page"))


class LinkValidationMixin:
    """
    Ensures that you cannot select both an external and an internal link.
    Used by both LinkBlock FooterLinkBlock
    """

    def clean(self, value):
        struct_value = super().clean(value)

        errors = {}
        page = value.get("page")
        external_link = value.get("external_link")

        if not page and not external_link:
            error = ErrorList(
                [ValidationError("You must specify either a page or an external link")]
            )
            errors["page"] = errors["external_link"] = error

        if page and external_link:
            error = ErrorList(
                [
                    ValidationError(
                        "You must specify either a page or an external link, not both"
                    )
                ]
            )
            errors["external_link"] = errors["page"] = error

        if errors:
            raise StructBlockValidationError(errors)
        return struct_value


class InternalLinkBlock(LinkValidationMixin, blocks.StructBlock):
    """
    Used to select links for the primary navigation (internal links only)
    """

    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(
        help_text="Leave blank to use the page's own title",
        required=False,
        label="Navigation text",
    )

    class Meta:
        value_class = LinkBlockStructValue


class LinkBlock(InternalLinkBlock):
    """
    Used to select links for the footer links (internal and external links)
    """

    external_link = blocks.URLBlock(required=False)

    class Meta:
        value_class = LinkBlockStructValue

    def clean(self, value):
        """
        Additional validation to ensure that a link title is specified for external links
        """
        struct_value = super().clean(value)

        errors = {}
        external_link = value.get("external_link")

        if not value.get("title") and external_link:
            error = ErrorList(
                [ValidationError("You must specify the link title for external links")]
            )
            errors["title"] = error

        if errors:
            raise StructBlockValidationError(errors)
        return struct_value


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
