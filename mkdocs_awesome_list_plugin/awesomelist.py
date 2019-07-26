import re
import sys
import uuid
from mkdocs.plugins import BasePlugin
from webpreview import web_preview


HTML = """
<div style="
    display: block;
    height: 102px;
    padding: 0;
    margin: 10px;
    border-width: 1px;
    border-color: #bfbfbf;
    border-style: solid;
    border-radius: 5px;
">
    <div style="float: left; padding: 0; margin: 0;">
        <img src="{}" style="height: 100px; padding: 0; margin: 0; border: none; margin-right: 16px;">
    </div>
    <div style="margin: 16px;">
        <span style="font-weight: bold;">{}</span><br>
        {}
    </div>
</div>
"""

class AwesomeList(BasePlugin):

    def __init__(self):
        super().__init__()
        self.social_cards = {}

    def on_page_markdown(self, markdown, **kwargs):
        copy = markdown
        extra_characters = 0
        for match in re.finditer("-[ ]\[(.*?)\]\((.*?)\)[ ]-[ ](.+?(?<=\.))", markdown):
            end_char  = match.span()[1]
            full_match = match.group()
            items = match.groups()
            try:
                title, description, image = ('title', 'description', 'https://avatars0.githubusercontent.com/u/21085506?s=400&v=4')  #web_preview(items[1], timeout=5)
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                print("\nError trying to retrieve data: {}".format(e))
                print("\tF: {}".format(full_match))
                print("\tT: {}".format(items[0]))
                print("\tU: {}".format(items[1]))
                print("\tD: {}".format(items[2]))
            else:
                print(".", end=" ")
                sys.stdout.flush()
                uniqueId = uuid.uuid4().hex
                self.social_cards[uniqueId] = HTML.format(image, title, description)
                injected_str = '{' + uniqueId +'}'
                copy = copy[:end_char + extra_characters] + injected_str + markdown[end_char:]
                extra_characters += len(injected_str)
        return copy

    def on_page_content(self, html, page, config, **kwargs):
        return html.format(**self.social_cards)
