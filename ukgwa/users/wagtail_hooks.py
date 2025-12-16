# fmt: off
from django.conf import settings
from django.urls import reverse

from wagtail import hooks
from wagtail.admin.menu import MenuItem

if getattr(settings, "ENABLE_DJANGO_DEFENDER", False):
    # Register shortcut to access django-defender's blocked list view within django admin
    class DjangoAdminMenuItem(MenuItem):
        def is_shown(self, request):
            return request.user.is_superuser

    @hooks.register("register_settings_menu_item")
    def register_locked_accounts_menu_item():
        return DjangoAdminMenuItem(
            "Locked accounts",
            reverse("defender_blocks_view"),
            icon_name="lock",
            order=601,
        )


@hooks.register("construct_main_menu")
def hide_documents_menu_item(request, menu_items):
    """Hide the Documents menu item from the admin sidebar."""
    menu_items[:] = [item for item in menu_items if item.name != "documents"]
# fmt: on
