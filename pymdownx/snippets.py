"""
Snippet ---8<---.

pymdownx.snippet
Inject snippets

MIT license.

Copyright (c) 2017 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import codecs
import os
import re

from markdown import Extension
from markdown.preprocessors import Preprocessor


class SnippetPreprocessor(Preprocessor):
    """Handle snippets in Markdown content."""

    RE_ALL_SNIPPETS = re.compile(
        r"""(?x)
        ^(?P<space>[ \t]*)
        (?P<all>
            (?P<inline_marker>-{2,}8<-{2,}[ ]+)
            (?P<snippet>(?:"(?:\\"|[^"\n])+?"|'(?:\\'|[^'\n])+?'))(?![ \t]) |
            (?P<block_marker>-{2,}8<-{2,})(?![ \t])
        )$
        """
    )

    RE_SNIPPET = re.compile(
        r"""(?x)
        ^(?P<space>[ \t]*)
        (?P<snippet>.*?)$
        """
    )

    def __init__(self, config, md):
        """Initialize."""

        self.base_path = config.get("base_path")
        self.encoding = config.get("encoding")
        self.tab_length = md.tab_length
        super().__init__()

    def parse_snippets(self, lines, file_name=None):
        """Parse snippets snippet."""

        new_lines = []
        inline = False
        block = False
        for line in lines:
            m = self.RE_ALL_SNIPPETS.match(line)
            if m:
                if block and m.group("inline_marker"):
                    # Don't use inline notation directly under a block.
                    # It's okay if inline is used again in sub file though.
                    continue
                elif m.group("inline_marker"):
                    # Inline
                    inline = True
                else:
                    # Block
                    block = not block
                    continue
            elif not block:
                # Not in snippet, and we didn't find an inline,
                # so just a normal line
                new_lines.append(line)
                continue

            if block and not inline:
                # We are in a block and we didn't just find a nested inline
                # So check if a block path
                m = self.RE_SNIPPET.match(line)

            if m:
                # Get spaces and snippet path.  Remove quotes if inline.
                space = m.group("space").replace("\t", " " * self.tab_length)
                path = (
                    m.group("snippet")[1:-1].strip()
                    if inline
                    else m.group("snippet").strip()
                )

                if not inline:
                    # Block path handling
                    if not path:
                        # Empty path line, insert a blank line
                        new_lines.append("")
                        continue
                if path.startswith("; "):
                    # path stats with '#', consider it commented out.
                    # We just removing the line.
                    continue

                snippet = os.path.join(self.base_path, path)
                if snippet and os.path.exists(snippet):
                    if snippet in self.seen:
                        # This is in the stack and we don't want an infinite loop!
                        continue
                    if file_name:
                        # Track this file.
                        self.seen.add(file_name)
                    try:
                        with codecs.open(snippet, "r", encoding=self.encoding) as f:
                            new_lines.extend(
                                [
                                    space + l2
                                    for l2 in self.parse_snippets(
                                        [l.rstrip("\r\n") for l in f], snippet
                                    )
                                ]
                            )
                    except Exception:  # pragma: no cover
                        pass
                    if file_name:
                        self.seen.remove(file_name)

        return new_lines

    def run(self, lines):
        """Process snippets."""

        self.seen = set()
        return self.parse_snippets(lines)


class SnippetExtension(Extension):
    """Snippet extension."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            "base_path": [".", 'Base path for snippet paths - Default: ""'],
            "encoding": ["utf-8", 'Encoding of snippets - Default: "utf-8"'],
        }

        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Register the extension."""

        self.md = md
        md.registerExtension(self)
        config = self.getConfigs()
        snippet = SnippetPreprocessor(config, md)
        md.preprocessors.add("snippet", snippet, ">normalize_whitespace")


def makeExtension(*args, **kwargs):
    """Return extension."""

    return SnippetExtension(*args, **kwargs)
