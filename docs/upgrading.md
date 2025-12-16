# Upgrading Wagtail guidelines

This document describes aspects of the system which should be given particular attention when upgrading Wagtail or its dependencies.

## Wagtail package dependencies

When adding new wagtail packages please include them below.

### Check these packages for updates

**Last tested for wagtail 7.1 upgrade** Comments in the pyproject.toml file may have more detailed information.

- wagtail-accessibility
- wagtail-factories (dev dependency)
- wagtail-storages

If you've pinned a dependency to a git tag, replace it with the official PyPI release version as soon as it becomes available.

## Overridden Wagtail core templates in this code base

We sometimes override Wagtail core templates and/or Wagtail core code to add custom functionality. When upgrading Wagtail, we need to check if the overridden templates or code base are still compatible with the new version of Wagtail. If not, we need to update the overridden templates or code base.

<!-- List overridden templates and code here -->

- None

## Critical paths

The following areas of functionality are critical paths for the site which don't have full automated tests and should be checked manually.

<!-- If this information is managed in a separate document, a link here will suffice -->

<!--
### 1. [Summary of critical path, e.g. 'Search']

[Description of the overall functionality covered]

- Step-by-step instructions for what to test and what the expected behaviour is
- Include details for edge cases as well as the general case
- Break this into separate subsections if there's a lot to cover
- Don't include anything which is already covered by automated testing, unless it's a prerequisite for a manual test
-->

- N/A

## Other considerations

As well as testing the critical paths, these areas of functionality should be checked:

<!--
 - ...
- Other places where you know extra maintenance or checks may be necessary
- This could be code which you know should be checked and possibly removed - e.g. because you've patched something until a fix is merged in a subsequent release
- Any previous fixes which may need to be updated/reapplied on subsequent upgrades
- Technical debt which could be affected by an upgrade
-->

- N/A
