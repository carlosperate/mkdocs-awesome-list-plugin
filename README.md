# MkDocs Awesome List Plugin

MkDocs Plugin to turn each entry in an
[Awesome List](https://github.com/topics/awesome) into a card, with the linked
page's preview image and favicon.

To use this plugin install it with pip in the same environment than MkDocs:

```
pip install mkdocs-awesomelist
```

Then add the following entry in the Mkdocs config file:

```yml
plugins:
  - awesome-list
```

## Options

```yml
plugins:
  - awesome-list:
      debug-log: false
      # Card style for every list, added as an `awesome-list--<style>` class
      default-style: media
      # Per-section styles, keyed by the heading anchor
      section-styles:
        libraries: index
```

The plugin includes CSS for two styles:

- `media`: a card per entry, with the preview image on the left. In lists narrower
  than 600px the description goes under the image instead.
- `index`: compact rows with the site's favicon, useful for long lists of repositories.

Any other style name only adds its class, for a theme to style.

## Markup

Entries are top-level list items that start with a web link, usually written as
`- [Name](url) - Description` (the description is optional).
The plugin keeps the list Markdown renders and adds classes and the fetched
data to it:

```html
<ul class="awesome-list awesome-list--media">
  <li class="awesome-entry" data-image="picture">
    <a class="awesome-entry__media" href="…"><img src="…"></a>
    <span class="awesome-entry__icon"><img src="…"></span>
    <span class="awesome-entry__header">
      <a class="awesome-entry__title" href="…"><img class="awesome-entry__favicon" src="…">Name</a>
      <span class="awesome-entry__domain">example.com</span>
    </span>
    <span class="awesome-entry__desc">Description</span>
    <ul class="awesome-entry__subs">
      <li class="awesome-entry__sub">
        <a href="…" title="Description">Name</a>
        <span class="awesome-entry__sub-desc">Description</span>
      </li>
    </ul>
  </li>
</ul>
```

- `data-image` is `picture`, `logo` (200px or smaller) or `none` (no
  image, or it couldn't be loaded). `awesome-entry__media` is only there when
  there is an image.
- `awesome-entry__icon` holds the favicon, or the entry's initial when the
  site has none. The same favicon is also in the title, when there is one.
- The default CSS stretches the title link over the entry, so the whole card is
  one click target; other links in it stay clickable above it.
- `awesome-entry__subs` holds the indented sub-entries, if any.

The default stylesheet, `assets/awesome-list/awesome-list.css`, is added before
any `extra_css`, so a theme can override its CSS custom properties or any rule.
