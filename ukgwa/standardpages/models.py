from django.conf import settings
from django.core.paginator import Paginator
from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.search import index

from ukgwa.core.blocks import StoryBlock
from ukgwa.core.mixins import HighlightedLinksMixin
from ukgwa.core.models import BasePage


class InformationPage(HighlightedLinksMixin, BasePage):
    template = "pages/standardpages/information_page.html"

    introduction = models.TextField(blank=True)
    body = StreamField(StoryBlock())

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
    ]

    content_panels = (
        BasePage.content_panels
        + [
            FieldPanel("introduction"),
            FieldPanel("body"),
        ]
        + HighlightedLinksMixin.get_highlighted_links_panels()
    )


class IndexPage(BasePage):
    template = "pages/standardpages/index_page.html"

    introduction = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [FieldPanel("introduction")]

    search_fields = BasePage.search_fields + [index.SearchField("introduction")]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        subpages = self.get_children().live().order_by("title")
        per_page = settings.DEFAULT_PER_PAGE
        page_number = request.GET.get("page")
        subpages = Paginator(subpages, per_page).get_page(page_number)

        context["subpages"] = subpages

        return context
