"""Tests for the AwesomeList MkDocs plugin."""

import re
import uuid
from unittest.mock import patch, MagicMock

import pytest

from mkdocs_awesome_list_plugin.awesomelist import (
    _resolve_and_validate_image,
    AwesomeList,
    HTML,
)


# ---------------------------------------------------------------------------
# _resolve_and_validate_image
# ---------------------------------------------------------------------------


class TestResolveAndValidateImage:
    """Tests for the image URL resolution helper."""

    def test_none_input(self):
        assert _resolve_and_validate_image(None, "https://example.com") is None

    def test_empty_string(self):
        assert _resolve_and_validate_image("", "https://example.com") is None

    def test_fully_qualified_http(self):
        url = "http://cdn.example.com/img.png"
        assert _resolve_and_validate_image(url, "https://example.com") == url

    def test_fully_qualified_https(self):
        url = "https://cdn.example.com/img.png"
        assert _resolve_and_validate_image(url, "https://example.com") == url

    @patch("mkdocs_awesome_list_plugin.awesomelist.requests.head")
    def test_protocol_relative(self, mock_head):
        mock_head.return_value = MagicMock(status_code=200)
        result = _resolve_and_validate_image(
            "//cdn.example.com/img.png", "https://example.com"
        )
        assert result == "https://cdn.example.com/img.png"

    @patch("mkdocs_awesome_list_plugin.awesomelist.requests.head")
    def test_absolute_path_resolved(self, mock_head):
        mock_head.return_value = MagicMock(status_code=200)
        result = _resolve_and_validate_image(
            "/assets/img.png", "https://example.com/page"
        )
        assert result == "https://example.com/assets/img.png"

    @patch("mkdocs_awesome_list_plugin.awesomelist.requests.head")
    def test_relative_path_resolved(self, mock_head):
        mock_head.return_value = MagicMock(status_code=200)
        result = _resolve_and_validate_image(
            "img.png", "https://example.com/page/"
        )
        assert result == "https://example.com/page/img.png"

    @patch("mkdocs_awesome_list_plugin.awesomelist.requests.head")
    def test_head_404_returns_none(self, mock_head):
        mock_head.return_value = MagicMock(status_code=404)
        result = _resolve_and_validate_image(
            "/missing.png", "https://example.com"
        )
        assert result is None

    @patch("mkdocs_awesome_list_plugin.awesomelist.requests.head")
    def test_head_network_error_returns_none(self, mock_head):
        mock_head.side_effect = Exception("connection refused")
        result = _resolve_and_validate_image(
            "/fail.png", "https://example.com"
        )
        assert result is None


# ---------------------------------------------------------------------------
# AwesomeList.on_page_markdown
# ---------------------------------------------------------------------------


class TestOnPageMarkdown:
    """Tests for markdown processing and social-card injection."""

    def _make_plugin(self, debug=False):
        plugin = AwesomeList()
        plugin.config = {"debug-log": debug}
        return plugin

    def test_no_matches_returns_unchanged(self):
        plugin = self._make_plugin()
        md = "# Hello\n\nJust some text."
        assert plugin.on_page_markdown(md) == md

    def test_plain_list_items_ignored(self):
        plugin = self._make_plugin()
        md = "- plain item without a link\n- another one"
        assert plugin.on_page_markdown(md) == md

    @patch("mkdocs_awesome_list_plugin.awesomelist._fetch_all_previews", new_callable=MagicMock)
    @patch("mkdocs_awesome_list_plugin.awesomelist.asyncio.set_event_loop")
    @patch("mkdocs_awesome_list_plugin.awesomelist.asyncio.new_event_loop")
    def test_single_entry_injects_placeholder(self, mock_new_loop, _mock_set, _mock_fetch):
        """A matching awesome-list line gets a UUID placeholder appended."""
        plugin = self._make_plugin()

        # Simulate the async fetch returning card data
        mock_loop = MagicMock()
        mock_new_loop.return_value = mock_loop
        mock_loop.run_until_complete.return_value = [
            (
                ("MicroPython", "https://micropython.org", "Python for MCUs"),
                "MicroPython",
                "Python for microcontrollers",
                "https://micropython.org/img.png",
            )
        ]

        md = "- [MicroPython](https://micropython.org) - Python for MCUs"
        result = plugin.on_page_markdown(md)

        # The original line should still be present
        assert "- [MicroPython](https://micropython.org) - Python for MCUs" in result
        # A UUID placeholder should have been appended
        assert re.search(r"\{[0-9a-f]{32}\}", result)
        # Plugin should have stored the rendered card
        assert len(plugin.social_cards) == 1

    @patch("mkdocs_awesome_list_plugin.awesomelist._fetch_all_previews", new_callable=MagicMock)
    @patch("mkdocs_awesome_list_plugin.awesomelist.asyncio.set_event_loop")
    @patch("mkdocs_awesome_list_plugin.awesomelist.asyncio.new_event_loop")
    def test_multiple_entries(self, mock_new_loop, _mock_set, _mock_fetch):
        """Multiple awesome-list lines each get their own placeholder."""
        plugin = self._make_plugin()

        mock_loop = MagicMock()
        mock_new_loop.return_value = mock_loop
        mock_loop.run_until_complete.return_value = [
            (
                ("Project A", "https://a.example.com", "Description A"),
                "Project A",
                "Desc A",
                None,
            ),
            (
                ("Project B", "https://b.example.com", "Description B"),
                "Project B",
                "Desc B",
                "https://b.example.com/img.png",
            ),
        ]

        md = (
            "- [Project A](https://a.example.com) - Description A\n"
            "- [Project B](https://b.example.com) - Description B"
        )
        result = plugin.on_page_markdown(md)

        placeholders = re.findall(r"\{[0-9a-f]{32}\}", result)
        assert len(placeholders) == 2
        assert len(plugin.social_cards) == 2

    @patch("mkdocs_awesome_list_plugin.awesomelist._fetch_all_previews", new_callable=MagicMock)
    @patch("mkdocs_awesome_list_plugin.awesomelist.asyncio.set_event_loop")
    @patch("mkdocs_awesome_list_plugin.awesomelist.asyncio.new_event_loop")
    def test_no_image_hides_img_style(self, mock_new_loop, _mock_set, _mock_fetch):
        """When no image is available, img_style should contain 'display: none'."""
        plugin = self._make_plugin()

        mock_loop = MagicMock()
        mock_new_loop.return_value = mock_loop
        mock_loop.run_until_complete.return_value = [
            (
                ("NoImg", "https://noimg.example.com", "No image here"),
                "NoImg",
                "No image",
                None,
            ),
        ]

        md = "- [NoImg](https://noimg.example.com) - No image here"
        plugin.on_page_markdown(md)

        card_html = list(plugin.social_cards.values())[0]
        assert "display: none" in card_html

    @patch("mkdocs_awesome_list_plugin.awesomelist._fetch_all_previews", new_callable=MagicMock)
    @patch("mkdocs_awesome_list_plugin.awesomelist.asyncio.set_event_loop")
    @patch("mkdocs_awesome_list_plugin.awesomelist.asyncio.new_event_loop")
    def test_fetch_exception_skips_entry(self, mock_new_loop, _mock_set, _mock_fetch):
        """If a preview fetch raises, the entry is skipped gracefully."""
        plugin = self._make_plugin()

        mock_loop = MagicMock()
        mock_new_loop.return_value = mock_loop
        mock_loop.run_until_complete.return_value = [
            Exception("timeout"),
        ]

        md = "- [Broken](https://broken.example.com) - Oops"
        result = plugin.on_page_markdown(md)

        # No placeholder injected for the failed entry
        assert not re.search(r"\{[0-9a-f]{32}\}", result)
        assert len(plugin.social_cards) == 0

    @patch("mkdocs_awesome_list_plugin.awesomelist._fetch_all_previews", new_callable=MagicMock)
    @patch("mkdocs_awesome_list_plugin.awesomelist.asyncio.set_event_loop")
    @patch("mkdocs_awesome_list_plugin.awesomelist.asyncio.new_event_loop")
    def test_fallback_title_and_description(self, mock_new_loop, _mock_set, _mock_fetch):
        """When fetched title/description are empty, use the markdown values."""
        plugin = self._make_plugin()

        mock_loop = MagicMock()
        mock_new_loop.return_value = mock_loop
        mock_loop.run_until_complete.return_value = [
            (
                ("FallbackName", "https://fb.example.com", "Fallback desc"),
                None,  # no title from web_preview
                None,  # no description from web_preview
                None,
            ),
        ]

        md = "- [FallbackName](https://fb.example.com) - Fallback desc"
        plugin.on_page_markdown(md)

        card_html = list(plugin.social_cards.values())[0]
        assert "FallbackName" in card_html
        assert "Fallback desc" in card_html


# ---------------------------------------------------------------------------
# AwesomeList.on_page_content
# ---------------------------------------------------------------------------


class TestOnPageContent:
    """Tests for the HTML post-processing step."""

    def test_replaces_placeholders_in_html(self):
        plugin = AwesomeList()
        uid = uuid.uuid4().hex
        plugin.social_cards[uid] = "<div>card</div>"
        html = f"<p>before</p>{{{uid}}}<p>after</p>"
        result = plugin.on_page_content(html, page=None, config=None)
        assert "<div>card</div>" in result
        assert f"{{{uid}}}" not in result

    def test_no_placeholders_passthrough(self):
        plugin = AwesomeList()
        html = "<p>nothing to replace</p>"
        result = plugin.on_page_content(html, page=None, config=None)
        assert result == html


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------


class TestHtmlTemplate:
    """Quick sanity checks on the card template."""

    def test_template_contains_placeholders(self):
        for key in ("url", "image", "title", "description", "img_style"):
            assert f"{{{key}}}" in HTML

    def test_template_renders(self):
        rendered = HTML.format(
            url="https://example.com",
            image="https://example.com/img.png",
            title="Example",
            description="An example",
            img_style="",
        )
        assert "https://example.com" in rendered
        assert "Example" in rendered
