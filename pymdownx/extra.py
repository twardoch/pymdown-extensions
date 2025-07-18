"""
Extra.

pymdown.extra
A wrapper that emulate PHP Markdown Extra.
Re-packages Python Markdowns 'extra' extensions,
but substitues a few extensions with PyMdown extensions:

    - fenced_code --> superfences
    - smartstrong --> betterem

MIT license.

Copyright (c) 2015 - 2017 Isaac Muse <isaacmuse@gmail.com>

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

from markdown import Extension

extra_extensions = [
    "pymdownx.betterem",
    "pymdownx.superfences",
    "markdown.extensions.footnotes",
    "markdown.extensions.attr_list",
    "markdown.extensions.def_list",
    "markdown.extensions.tables",
    "markdown.extensions.abbr",
    "pymdownx.extrarawhtml",
]

extra_extension_configs = {}


class ExtraExtension(Extension):
    """Add various extensions to Markdown class."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = kwargs.pop("configs", {})
        self.config.update(extra_extension_configs)
        self.config.update(kwargs)

    def extendMarkdown(self, md, md_globals):
        """Register extension instances."""

        md.registerExtensions(extra_extensions, self.config)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return ExtraExtension(*args, **kwargs)
