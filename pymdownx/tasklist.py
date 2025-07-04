"""
Tasklist.

pymdownx.tasklist
An extension for Python Markdown.
Github style tasklists

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

import re

from markdown import Extension
from markdown.treeprocessors import Treeprocessor

RE_CHECKBOX = re.compile(r"^(?P<checkbox> *\[(?P<state>(?:x|X| ){1})\] +)(?P<line>.*)")


def get_checkbox(state, custom_checkbox=False):
    """Get checkbox tag."""

    if custom_checkbox:
        return (
            '<label class="task-list-control">'
            + '<input type="checkbox" disabled%s/>'
            % (" checked" if state.lower() == "x" else "")
            + '<span class="task-list-indicator"></span></label> '
        )
    return '<input type="checkbox" disabled%s> ' % (
        " checked" if state.lower() == "x" else ""
    )


class TasklistTreeprocessor(Treeprocessor):
    """Tasklist Treeprocessor that finds lists with checkboxes."""

    def inline(self, li):
        """Search for checkbox directly in li tag."""

        found = False
        m = RE_CHECKBOX.match(li.text)
        if m is not None:
            li.text = self.markdown.htmlStash.store(
                get_checkbox(m.group("state"), self.custom_checkbox), safe=True
            ) + m.group("line")
            found = True
        return found

    def sub_paragraph(self, li):
        """Search for checkbox in sub-paragraph."""

        found = False
        if len(li):
            first = list(li)[0]
            if first.tag == "p" and first.text is not None:
                m = RE_CHECKBOX.match(first.text)
                if m is not None:
                    first.text = self.markdown.htmlStash.store(
                        get_checkbox(m.group("state"), self.custom_checkbox), safe=True
                    ) + m.group("line")
                    found = True
        return found

    def run(self, root):
        """Find list items that start with [ ] or [x] or [X]."""

        self.custom_checkbox = bool(self.config["custom_checkbox"])
        parent_map = {c: p for p in root.iter() for c in p}
        task_items = []
        lilinks = root.iter("li")
        for li in lilinks:
            if li.text is None or li.text == "":
                if not self.sub_paragraph(li):
                    continue
            elif not self.inline(li):
                continue

            # Checkbox found
            c = li.attrib.get("class", "")
            classes = [] if c == "" else c.split()
            classes.append("task-list-item")
            li.attrib["class"] = " ".join(classes)
            task_items.append(li)

        for li in task_items:
            parent = parent_map[li]
            c = parent.attrib.get("class", "")
            classes = [] if c == "" else c.split()
            if "task-list" not in classes:
                classes.append("task-list")
            parent.attrib["class"] = " ".join(classes)
        return root


class TasklistExtension(Extension):
    """Tasklist extension."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            "custom_checkbox": [
                False,
                "Add an empty label tag after the input tag to allow for custom styling - Default: False",
            ],
            "delete": [True, "Enable delete - Default: True"],
            "subscript": [True, "Enable subscript - Default: True"],
        }

        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add GithubChecklistsTreeprocessor to Markdown instance."""

        tasklist = TasklistTreeprocessor(md)
        tasklist.config = self.getConfigs()
        md.treeprocessors.add("task-list", tasklist, ">inline")
        md.registerExtension(self)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return TasklistExtension(*args, **kwargs)
