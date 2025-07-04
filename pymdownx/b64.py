"""
B64.

An extension for Python Markdown.
Given an absolute base path, this extension searches for img tags,
and if the images are local, will embed the images in base64.

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

import base64
import os
import re

from markdown import Extension
from markdown.postprocessors import Postprocessor

from . import util

# import traceback

RE_SLASH_WIN_DRIVE = re.compile(r"^/[A-Za-z]{1}:/.*")

file_types = {
    (".png",): "image/png",
    (".jpg", ".jpeg"): "image/jpeg",
    (".gif",): "image/gif",
}

RE_TAG_HTML = re.compile(
    r"""(?xus)
    (?:
        (?P<comments>(\r?\n?\s*)<!--[\s\S]*?-->(\s*)(?=\r?\n)|<!--[\s\S]*?-->)|
        (?P<open><(?P<tag>img))
        (?P<attr>(?:\s+[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)
        (?P<close>\s*(?:\/?)>)
    )
    """
)

RE_TAG_LINK_ATTR = re.compile(
    r"""(?xus)
    (?P<attr>
        (?:
            (?P<name>\s+src\s*=\s*)
            (?P<path>"[^"]*"|'[^']*')
        )
    )
    """
)


def repl_path(m, base_path):
    """Replace path with b64 encoded data."""

    link = m.group(0)
    try:
        scheme, netloc, path, params, query, fragment, is_url, is_absolute = (
            util.parse_url(m.group("path")[1:-1])
        )
        if not is_url:
            path = util.url2pathname(path).replace("\\", "/")
            # Adjust /c:/ to c:/.
            # If some 'nix OS is using a folder formated like a windows drive,
            # too bad :).
            if scheme == "file" and RE_SLASH_WIN_DRIVE.match(path):
                path = path[1:]

        if is_absolute:
            file_name = os.path.normpath(path)
        else:
            file_name = os.path.normpath(os.path.join(base_path, path))

        if os.path.exists(file_name):
            ext = os.path.splitext(file_name)[1].lower()
            for b64_ext in file_types:
                if ext in b64_ext:
                    with open(file_name, "rb") as f:
                        link = ' src="data:{};base64,{}"'.format(
                            file_types[b64_ext],
                            base64.b64encode(f.read()).decode("ascii"),
                        )
                    break

    except Exception:  # pragma: no cover
        # Parsing crashed and burned; no need to continue.
        pass

    return link


def repl(m, base_path):
    """Replace."""

    if m.group("comments"):
        tag = m.group("comments")
    else:
        tag = m.group("open")
        tag += RE_TAG_LINK_ATTR.sub(
            lambda m2: repl_path(m2, base_path), m.group("attr")
        )
        tag += m.group("close")
    return tag


class B64Postprocessor(Postprocessor):
    """Post processor for B64."""

    def run(self, text):
        """Find and replace paths with base64 encoded file."""

        basepath = self.config["base_path"]
        text = RE_TAG_HTML.sub(lambda m: repl(m, basepath), text)
        return text


class B64Extension(Extension):
    """B64 extension."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            "base_path": [
                ".",
                'Base path for b64 to use to resolve paths - Default: "."',
            ]
        }

        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add B64Treeprocessor to Markdown instance."""

        b64 = B64Postprocessor(md)
        b64.config = self.getConfigs()
        md.postprocessors.add("b64", b64, "_end")
        md.registerExtension(self)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return B64Extension(*args, **kwargs)
