# Card Component

Versatile card for content listings.
Renders as an `<li>` containing an `<article>` - must be used within a `<ul>` parent.

## Usage

```django
<ul>
    {% include "components/card/card.html" with title=page.title url=page_url %}
</ul>
```

## Required Parameters

- `title`: Card heading text
- `url`: Link destination

## Optional Parameters

- `summary`: Summary text below the heading
- `category`: Category label above the heading
- `source_url`: Source URL text below the summary
- `modifier`: BEM modifier class (e.g., "listing", "recently-archived")
- `clickable`: Boolean to add clickable modifier (makes entire card clickable)
- `heading_level`: Heading level (default: "h2")
- `grid_classes`: Tailwind grid classes (e.g., "col-span-12 md:col-span-6")

