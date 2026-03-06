import re
import sys
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urljoin

import requests
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from webpreview import web_preview

HTML = """
<div style="
    display: block;
    max-height: 122px;
    padding: 0px;
    margin: 12px;
    border-width: 1px;
    border-color: #bfbfbf;
    border-style: solid;
    border-radius: 16px;
    box-shadow: 0px 3px 6px rgb(0 0 0 / 7%);
    overflow: hidden;
    background-color: #fbfbfb;
">
    <div style="float: left; padding: 0; margin: 0; {img_style}">
        <a href="{url}" target="_blank" style="border: none">
            <img src="{image}" style="height: 120px; max-width: 150px; object-fit: cover; padding: 0; margin: 0; border: none; margin-right: 16px;">
        </a>
    </div>
    <div style="margin: 8px 24px; line-height: 1.2;">
        <a href="{url}" target="_blank"><span style="font-weight: bold; line-height: 1.8;">{title}</span></a>
        <br>
        <span style="font-size: calc(100% - 1px); line-height: 1.5;">{description}</span>
    </div>
</div>
"""


def _resolve_and_validate_image(image, page_url):
    """Resolve relative/absolute image URLs and validate they exist."""
    if not image:
        return None
    parsed = urlparse(image)
    # Fully qualified URL (http/https) — keep as-is
    if parsed.scheme in ("http", "https"):
        return image
    # Protocol-relative (//cdn.example.com/...)
    if image.startswith("//"):
        image = "https:" + image
    # Absolute path (/assets/img/...) or relative path
    else:
        image = urljoin(page_url, image)
    # Verify the resolved image URL exists
    try:
        resp = requests.head(image, timeout=5, allow_redirects=True)
        if resp.status_code < 400:
            return image
        print(f"\n  WARNING: Image returned {resp.status_code}: {image}")
    except Exception as e:
        print(f"\n  WARNING: Could not reach image: {image} ({e})")
    return None


async def _fetch_preview(entry, executor):
    """Fetch a single web preview in a thread executor."""
    loop = asyncio.get_running_loop()
    name, url, desc = entry
    title, description, image = await loop.run_in_executor(
        executor, lambda: web_preview(url, timeout=10)
    )
    image = _resolve_and_validate_image(image, url)
    return (entry, title, description, image)


async def _fetch_all_previews(entries):
    """Fetch all web previews in parallel using a thread pool."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        tasks = [
            asyncio.ensure_future(_fetch_preview(entry, executor))
            for entry in entries
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)


class AwesomeList(BasePlugin):

    config_scheme = (
        ("debug-log", config_options.Type(bool, default=False)),
        ("card-style", config_options.Choice(("append", "replace"), default="append")),
    )

    def __init__(self):
        super().__init__()
        self.social_cards = {}

    def on_page_markdown(self, markdown, **kwargs):
        # Collect all link matches first
        matches = list(
            re.finditer(r"^- \[(.*?)\]\((.*?)\) - (.+)$", markdown, re.MULTILINE)
        )
        if not matches:
            return markdown

        # Build the list of entries to fetch (name, url, description)
        entries = []
        for match in matches:
            items = match.groups()
            entries.append((items[0], items[1], items[2]))

        # Fetch all web previews in parallel
        print(f"\n[AwesomeList] Fetching {len(entries)} social cards...", end=" ")
        sys.stdout.flush()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(_fetch_all_previews(entries))
        finally:
            loop.close()

        # Map url -> fetched card data (or None on error)
        card_data = {}
        for result in results:
            if isinstance(result, Exception):
                print(f"\n[AwesomeList] Error fetching preview: {result}")
                continue
            entry, title, description, image = result
            card_data[entry[1]] = (title, description, image)
            if self.config["debug-log"]:
                print(f"\n  [{entry[0]}]")
                print(f"    URL:   {entry[1]}")
                print(f"    Title: {title}")
                print(f"    Desc:  {description}")
                print(f"    Image: {image}")
            sys.stdout.flush()
        print()

        # Inject social card placeholders into the markdown
        replace_mode = self.config.get("card-style", "append") == "replace"
        copy = markdown
        extra_characters = 0
        for match in matches:
            start_char = match.span()[0]
            end_char = match.span()[1]
            items = match.groups()
            url = items[1]

            if url not in card_data:
                continue

            title, description, image = card_data[url]
            if replace_mode:
                # Use the awesome-list entry text, not the OG metadata
                card_options = {
                    "title": items[0],
                    "description": items[2],
                    "url": url,
                }
            else:
                # Use the OG metadata title and description
                card_options = {
                    "title": title or items[0],
                    "description": description or items[2],
                    "url": url,
                }
            if not image:
                card_options["img_style"] = "display: none"
                card_options["image"] = ""
            else:
                card_options["img_style"] = ""
                card_options["image"] = image

            uniqueId = uuid.uuid4().hex
            self.social_cards[uniqueId] = HTML.format(**card_options)
            injected_str = '{' + uniqueId + '}'

            if replace_mode:
                # Replace the entire awesome-list line with the placeholder
                adj_start = start_char + extra_characters
                adj_end = end_char + extra_characters
                copy = copy[:adj_start] + injected_str + copy[adj_end:]
                extra_characters += len(injected_str) - (end_char - start_char)
            else:
                # Append the placeholder after the line
                adj_end = end_char + extra_characters
                copy = copy[:adj_end] + injected_str + copy[adj_end:]
                extra_characters += len(injected_str)

        return copy

    def on_page_content(self, html, page, config, **kwargs):
        return html.format(**self.social_cards)
