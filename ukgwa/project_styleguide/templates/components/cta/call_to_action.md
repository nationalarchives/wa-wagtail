# Call to Action Component

This template can be used in different places: in a streamfield block or directly in a page template.

## Usage

```django
{% include "components/cta/call_to_action.html" with call_to_action=call_to_action %}
```

## Parameters

- `call_to_action`: A call to action object with the following properties:
  - `title`: The heading text
  - `summary`: Rich text content
  - `image`: Optional Wagtail image object
  - `get_link_url`: The link URL
  - `get_link_text`: The button text

