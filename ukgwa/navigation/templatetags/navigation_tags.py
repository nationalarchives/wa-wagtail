from django import template

register = template.Library()


# Primary nav snippets
@register.inclusion_tag("components/navigation/primary_nav.html", takes_context=True)
def primary_nav(context):
    request = context["request"]
    page = context.get("page")

    # Get ancestor IDs to check if current page is within a nav item's subtree
    ancestor_ids = set()
    if page and hasattr(page, "get_ancestors"):
        ancestor_ids = set(page.get_ancestors().values_list("pk", flat=True))

    return {
        "primary_nav": context["settings"]["navigation"][
            "NavigationSettings"
        ].primary_navigation,
        "request": request,
        "current_page": page,
        "ancestor_ids": ancestor_ids,
    }


# Secondary nav snippets
@register.inclusion_tag("components/navigation/secondary_nav.html", takes_context=True)
def secondary_nav(context):
    request = context["request"]
    return {
        "secondary_nav": context["settings"]["navigation"][
            "NavigationSettings"
        ].secondary_navigation,
        "request": request,
    }


# Footer nav snippets
@register.inclusion_tag("components/navigation/footer_nav.html", takes_context=True)
def footer_nav(context):
    request = context["request"]
    return {
        "footer_nav": context["settings"]["navigation"][
            "NavigationSettings"
        ].footer_navigation,
        "request": request,
    }


@register.inclusion_tag("components/navigation/sidebar.html", takes_context=True)
def sidebar(context):
    page = context["page"]

    # Always show "level 2" items - children of the section (depth 3)
    # Wagtail depth: 1=Root, 2=Home, 3=Section, 4=Pages under section
    section = None

    if page.depth >= 3:
        # Find the section ancestor at depth 3
        for ancestor in page.get_ancestors():
            if ancestor.depth == 3:
                section = ancestor
                break

        # If current page is the section itself (depth 3)
        if section is None and page.depth == 3:
            section = page

    if section:
        # Get children of the section (the "level 2" items)
        siblings = section.get_children().live().public().in_menu()
        parent = section
    else:
        # Fallback for pages at depth 2 or less
        siblings = page.get_siblings().live().public().in_menu()
        parent = page.get_parent()

    # Get ancestor IDs to check if current page is within a sibling's subtree
    ancestor_ids = set(page.get_ancestors().values_list("pk", flat=True))

    # Get sidebar_cta from page if available, or from context
    sidebar_cta = getattr(page, "sidebar_cta", None) or context.get("sidebar_cta")

    return {
        "siblings": siblings,
        "parent": parent,
        "current_page": page,
        "ancestor_ids": ancestor_ids,
        "request": context["request"],
        "sidebar_cta": sidebar_cta,
    }


# Footer nav snippets
@register.inclusion_tag("components/navigation/footer_links.html", takes_context=True)
def footer_links(context):
    request = context["request"]
    return {
        "footer_links": context["settings"]["navigation"][
            "NavigationSettings"
        ].footer_links,
        "request": request,
    }


# Footer nav snippets
@register.inclusion_tag(
    "components/navigation/footer_logo_cloud.html", takes_context=True
)
def footer_logo_cloud(context):
    request = context["request"]
    return {
        "footer_logos": context["settings"]["navigation"][
            "NavigationSettings"
        ].footer_logo_cloud,
        "request": request,
    }
