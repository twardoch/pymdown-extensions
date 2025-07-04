"""
Path Converter.

pymdownx.pathconverter
An extension for Python Markdown.

An extension to covert tag paths to relative or absolute:

Given an absolute base and a target relative path, this extension searches for file
references that are relative and converts them to a path relative
to the base path.

-or-

Given an absolute base path, this extension searches for file
references that are relative and converts them to absolute paths.

MIT license.

Copyright (c) 2014 - 2017 Isaac Muse <isaacmuse@gmail.com>

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

import os
import re

from markdown import Extension
from markdown.postprocessors import Postprocessor

from . import util

RE_TAG_HTML = r"""(?xus)
    (?:
        (?P<comments>(\r?\n?\s*)<!--[\s\S]*?-->(\s*)(?=\r?\n)|<!--[\s\S]*?-->)|
        (?P<open><(?P<tag>(?:%s)))
        (?P<attr>(?:\s+[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)
        (?P<close>\s*(?:\/?)>)
    )
    """

RE_TAG_LINK_ATTR = re.compile(
    r"""(?xus)
    (?P<attr>
        (?:
            (?P<name>\s+(?:href|src)\s*=\s*)
            (?P<path>"[^"]*"|'[^']*')
        )
    )
    """
)


def repl_relative(m, base_path, relative_path):
    """Replace path with relative path."""

    link = m.group(0)
    try:
        scheme, netloc, path, params, query, fragment, is_url, is_absolute = (
            util.parse_url(m.group("path")[1:-1])
        )

        if not is_url:
            # Get the absolute path of the file or return
            # if we can't resolve the path
            path = util.url2pathname(path)
            abs_path = None
            if not is_absolute:
                # Convert current relative path to absolute
                temp = os.path.normpath(os.path.join(base_path, path))
                abs_path = temp.replace("\\", "/")

                # Convert the path, url encode it, and format it as a link
                path = util.pathname2url(
                    os.path.relpath(abs_path, relative_path).replace("\\", "/")
                )
                link = '{}"{}"'.format(
                    m.group("name"),
                    util.urlunparse((scheme, netloc, path, params, query, fragment)),
                )
    except Exception:  # pragma: no cover
        # Parsing crashed and burned; no need to continue.
        pass

    return link


def repl_absolute(m, base_path):
    """Replace path with absolute path."""

    link = m.group(0)
    try:
        scheme, netloc, path, params, query, fragment, is_url, is_absolute = (
            util.parse_url(m.group("path")[1:-1])
        )

        if not is_absolute and not is_url:
            path = util.url2pathname(path)
            temp = os.path.normpath(os.path.join(base_path, path))
            path = util.pathname2url(temp.replace("\\", "/"))
            link = '{}"{}"'.format(
                m.group("name"),
                util.urlunparse((scheme, netloc, path, params, query, fragment)),
            )
    except Exception:  # pragma: no cover
        # Parsing crashed and burned; no need to continue.
        pass

    return link


def repl(m, base_path, rel_path=None):
    """Replace."""

    if m.group("comments"):
        tag = m.group("comments")
    else:
        tag = m.group("open")
        if rel_path is None:
            tag += RE_TAG_LINK_ATTR.sub(
                lambda m2: repl_absolute(m2, base_path), m.group("attr")
            )
        else:
            tag += RE_TAG_LINK_ATTR.sub(
                lambda m2: repl_relative(m2, base_path, rel_path), m.group("attr")
            )
        tag += m.group("close")
    return tag


class PathConverterPostprocessor(Postprocessor):
    """Post process to find tag lings to convert."""

    def run(self, text):
        """Find and convert paths."""

        basepath = self.config["base_path"]
        relativepath = self.config["relative_path"]
        absolute = bool(self.config["absolute"])
        tags = re.compile(RE_TAG_HTML % "|".join(self.config["tags"].split()))
        if not absolute and basepath and relativepath:
            text = tags.sub(lambda m: repl(m, basepath, relativepath), text)
        elif absolute and basepath:
            text = tags.sub(lambda m: repl(m, basepath), text)
        return text


class PathConverterExtension(Extension):
    """PathConverter extension."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            "base_path": ["", 'Base path used to find files - Default: ""'],
            "relative_path": [
                "",
                'Path that files will be relative to (not needed if using absolute) - Default: ""',
            ],
            "absolute": [
                False,
                "Paths are absolute by default; disable for relative - Default: False",
            ],
            "tags": [
                "img script a link",
                "tags to convert src and/or href in - Default: 'img scripts a link'",
            ],
        }

        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add PathConverterPostprocessor to Markdown instance."""

        rel_path = PathConverterPostprocessor(md)
        rel_path.config = self.getConfigs()
        md.postprocessors.add("path-converter", rel_path, "_end")
        md.registerExtension(self)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return PathConverterExtension(*args, **kwargs)
