import re
import sys
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

    def on_page_markdown(self, markdown, **kwargs):
        copy = markdown
        extra_characters = 0
        for match in re.finditer("-[ ]\[(.*?)\]\((.*?)\)[ ]-[ ](.+?(?<=\.))", markdown):
            end_char  = match.span()[1]
            full_match = match.group()
            items = match.groups()
            # print(end_char, items)
            try:
                title, description, image = web_preview(items[1], timeout=1)
            except WebpreviewException:
                print('\nCould not retrieve data.\n\tF: {}\n\tT: {}\n\tU: {}\n\tD: {}'.format(full_match, items[0], items[1], items[2]))
            else:
                # print('Parsed:{}'.format(full_match))
                print(".", end=" ")
                sys.stdout.flush()
                str_to_copy = HTML.format(image, title, description)
                #str_to_copy = '\nhi\n'
                copy = copy[:end_char + extra_characters] + str_to_copy + markdown[end_char:]
                extra_characters += len(str_to_copy)
        return copy
