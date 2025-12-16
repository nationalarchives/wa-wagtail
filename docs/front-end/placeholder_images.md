## Placeholder images in the pattern library

When using the pattern library, use the custom YAML tag `!testimage` in your mocked context to inject a random placeholder value.

```yaml
context:
  pages:
    - title: Test page
      listing_url: !testimage
```

Images are loaded from the `project_styleguide/tests/assets/` directory on first use and are all linked to a collection named `pattern_library`.
If you need different images you can add them to the `pattern_library` collection and they'll automatically be picked up.

## Using Picsum for placeholder images

Alternatively, if all you need is a URL you can use the picsum.photos service.

The benefits of picsum:

- Allows webp
- Does not rely on reading cross-site cookies like Unsplash
- Faster than Unsplash

You can choose a specific image by browsing their library at https://picsum.photos/images Or use a random image: https://picsum.photos/540/190.webp

Generate a selection of images in different formats, all using the same seed image:

https://picsum.photos/seed/picsum/200/300.webp https://picsum.photos/seed/picsum/1000/1000.webp https://picsum.photos/seed/picsum/2900/300.webp
