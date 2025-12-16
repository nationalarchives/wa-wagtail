from django.test import RequestFactory, TestCase, override_settings

from wagtail.models import Site

from ukgwa.core.context_processors import global_vars
from ukgwa.core.models import Tracking


class GlobalVarsContextProcessorTest(TestCase):
    @override_settings(
        BASE_DOMAIN="example.com",
    )
    def test_when_no_tracking_settings_defined(self):
        request = RequestFactory().get("/")
        self.assertEqual(
            global_vars(request),
            {
                "GOOGLE_TAG_MANAGER_ID": "",
                "SEO_NOINDEX": False,
                "LANGUAGE_CODE": "en-gb",
                "BASE_DOMAIN": "example.com",
            },
        )

    @override_settings(
        BASE_DOMAIN="example.com",
    )
    def test_when_tracking_settings_defined(self):
        Tracking.objects.create(
            site=Site.objects.get(is_default_site=True),
            google_tag_manager_id="GTM-123456",
        )
        request = RequestFactory().get("/")
        self.assertEqual(
            global_vars(request),
            {
                "GOOGLE_TAG_MANAGER_ID": "GTM-123456",
                "SEO_NOINDEX": False,
                "LANGUAGE_CODE": "en-gb",
                "BASE_DOMAIN": "example.com",
            },
        )
