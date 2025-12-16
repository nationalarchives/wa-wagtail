import wagtail_factories

from ukgwa.home.models import HomePage


class HomePageFactory(wagtail_factories.PageFactory):
    title = "Home"

    class Meta:
        model = HomePage
