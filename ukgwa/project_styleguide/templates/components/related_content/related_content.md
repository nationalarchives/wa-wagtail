# Related Content Component

Related content / content listing component.

## Usage

```django
{% include "components/related_content/related_content.html" with related_pages=pages %}
```

## Parameters

- `heading`: Custom heading text (default: "Also of interest")
- `heading_id`: Custom ID for the heading (default: "related-content-heading")
- `intro`: Optional intro text below the heading
- `modifier`: BEM modifier class (e.g., "archive-highlights", "recently-archived")
- `related_pages`: List of page objects to display

