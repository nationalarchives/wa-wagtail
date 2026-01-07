# Alert Banner Component

Displays a site-wide notification banner with an icon and message.
Supports three modifiers: warning, info, and positive.

## Usage

```django
{% include "components/alert_banner/alert_banner.html" with alert_banner=alert_banner %}
```

## Context

- `alert_banner`: object containing:
  - `message`: The text to display
  - `modifier`: One of 'warning', 'info', or 'positive' (default: 'warning')

