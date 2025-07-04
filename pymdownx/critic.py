"""
Critic.

pymdownx.critic
Parses critic markup and outputs the file in a more visual HTML.
Must be the last extension loaded.

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
from markdown.postprocessors import Postprocessor
from markdown.preprocessors import Preprocessor

STX = "\u0002"
ETX = "\u0003"
CRITIC_KEY = "czjqqkd:%s"
CRITIC_PLACEHOLDER = CRITIC_KEY % r"[0-9]+"
SINGLE_CRITIC_PLACEHOLDER = r"{stx}(?P<key>{key}){etx}".format(
    key=CRITIC_PLACEHOLDER, stx=STX, etx=ETX
)
CRITIC_PLACEHOLDERS = r"""(?x)
(?:
    (?P<block>\<p\>(?P<block_keys>(?:{stx}{key}{etx})+)\</p\>) |
    {single}
)
""".format(key=CRITIC_PLACEHOLDER, single=SINGLE_CRITIC_PLACEHOLDER, stx=STX, etx=ETX)
ALL_CRITICS = r"""(?x)
((?P<critic>(?P<open>\{)
    (?:
        (?P<ins_open>\+{2})
        (?P<ins_text>.*?)
        (?P<ins_close>\+{2})

      | (?P<del_open>\-{2})
        (?P<del_text>.*?)
        (?P<del_close>\-{2})

      | (?P<mark_open>\={2})
        (?P<mark_text>.*?)
        (?P<mark_close>\={2})

      | (?P<comment>
            (?P<com_open>\>{2})
            (?P<com_text>.*?)
            (?P<com_close>\<{2})
        )

      | (?P<sub_open>\~{2})
        (?P<sub_del_text>.*?)
        (?P<sub_mid>\~\>)
        (?P<sub_ins_text>.*?)
        (?P<sub_close>\~{2})
    )
(?P<close>\})))
"""

RE_CRITIC = re.compile(ALL_CRITICS, re.DOTALL)
RE_CRITIC_PLACEHOLDER = re.compile(CRITIC_PLACEHOLDERS)
RE_CRITIC_SUB_PLACEHOLDER = re.compile(SINGLE_CRITIC_PLACEHOLDER)
RE_CRITIC_BLOCK = re.compile(r'((?:ins|del|mark)\s+)(class=([\'"]))(.*?)(\3)')
RE_BLOCK_SEP = re.compile(r"^\n{2,}$")


class CriticStash:
    """Stach critic marks until ready."""

    def __init__(self, stash_key):
        """Initialize."""

        self.stash_key = stash_key
        self.stash = {}
        self.count = 0

    def __len__(self):  # pragma: no cover
        """Get length of stash."""
        return len(self.stash)

    def get(self, key, default=None):
        """Get the specified item from the stash."""

        code = self.stash.get(key, default)
        return code

    def remove(self, key):  # pragma: no cover
        """Remove the specified item from the stash."""

        del self.stash[key]

    def store(self, code):
        """
        Store the code in the stash with the placeholder.

        Return placeholder.
        """
        key = self.stash_key % str(self.count)
        self.stash[key] = code
        self.count += 1
        return STX + key + ETX

    def clear(self):
        """Clear the stash."""

        self.stash = {}
        self.count = 0


class CriticsPostprocessor(Postprocessor):
    """Handle cleanup on postprocess for viewing critic marks."""

    def __init__(self, critic_stash):
        """Initialize."""

        super().__init__()
        self.critic_stash = critic_stash

    def subrestore(self, m):
        """Replace all critic tags in the paragraph block <p>(critic del close)(critic ins close)</p> etc."""
        content = None
        key = m.group("key")
        if key is not None:
            content = self.critic_stash.get(key)
        return content

    def block_edit(self, m):
        """Handle block edits."""

        if "break" in m.group(4).split(" "):
            return m.group(0)
        else:
            return m.group(1) + m.group(2) + m.group(4) + " block" + m.group(5)

    def restore(self, m):
        """Replace placeholders with actual critic tags."""

        content = None
        if m.group("block_keys") is not None:
            content = RE_CRITIC_SUB_PLACEHOLDER.sub(
                self.subrestore, m.group("block_keys")
            )
            if content is not None:
                content = RE_CRITIC_BLOCK.sub(self.block_edit, content)
        else:
            text = self.critic_stash.get(m.group("key"))
            if text is not None:
                content = text
        return content if content is not None else m.group(0)

    def run(self, text):
        """Replace critic placeholders."""

        text = RE_CRITIC_PLACEHOLDER.sub(self.restore, text)

        return text


class CriticViewPreprocessor(Preprocessor):
    """Handle viewing critic marks in Markdown content."""

    def __init__(self, critic_stash):
        """Initialize."""

        super().__init__()
        self.critic_stash = critic_stash

    def _ins(self, text):
        """Handle critic inserts."""

        if RE_BLOCK_SEP.match(text):
            return "\n\n%s\n\n" % self.critic_stash.store(
                '<ins class="critic break">&nbsp;</ins>'
            )
        return (
            self.critic_stash.store('<ins class="critic">')
            + text
            + self.critic_stash.store("</ins>")
        )

    def _del(self, text):
        """Hanlde critic deletes."""

        if RE_BLOCK_SEP.match(text):
            return self.critic_stash.store('<del class="critic break">&nbsp;</del>')
        return (
            self.critic_stash.store('<del class="critic">')
            + text
            + self.critic_stash.store("</del>")
        )

    def _mark(self, text):
        """Handle critic marks."""

        return (
            self.critic_stash.store('<mark class="critic">')
            + text
            + self.critic_stash.store("</mark>")
        )

    def _comment(self, text):
        """Handle critic comments."""

        return self.critic_stash.store(
            '<span class="critic comment">'
            + self.html_escape(text, strip_nl=True)
            + "</span>"
        )

    def critic_view(self, m):
        """Insert appropriate HTML to tags to visualize Critic marks."""

        if m.group("ins_open"):
            return self._ins(m.group("ins_text"))
        elif m.group("del_open"):
            return self._del(m.group("del_text"))
        elif m.group("sub_open"):
            return self._del(m.group("sub_del_text")) + self._ins(
                m.group("sub_ins_text")
            )
        elif m.group("mark_open"):
            return self._mark(m.group("mark_text"))
        elif m.group("com_open"):
            return self._comment(m.group("com_text"))

    def critic_parse(self, m):
        """
        Normal critic parser.

        Either removes accepted or rejected crtic marks and replaces with the opposite.
        Comments are removed and marks are replaced with their content.
        """
        accept = self.config["mode"] == "accept"
        if m.group("ins_open"):
            return m.group("ins_text") if accept else ""
        elif m.group("del_open"):
            return "" if accept else m.group("del_text")
        elif m.group("mark_open"):
            return m.group("mark_text")
        elif m.group("com_open"):
            return ""
        elif m.group("sub_open"):
            return m.group("sub_ins_text") if accept else m.group("sub_del_text")

    def html_escape(self, txt, strip_nl=False):
        """Basic html escaping."""

        txt = txt.replace("&", "&amp;")
        txt = txt.replace("<", "&lt;")
        txt = txt.replace(">", "&gt;")
        txt = txt.replace('"', "&quot;")
        txt = txt.replace("\n", "<br>" if not strip_nl else " ")
        return txt

    def run(self, lines):
        """Process critic marks."""

        # Determine processor type to use
        if self.config["mode"] == "view":
            processor = self.critic_view
        else:
            processor = self.critic_parse

        # Find and process critic marks
        text = RE_CRITIC.sub(processor, "\n".join(lines))

        return text.split("\n")


class CriticExtension(Extension):
    """Critic extension."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            "mode": [
                "view",
                "Critic mode to run in ('view', 'accept', or 'reject') - Default: view ",
            ],
            "raw_view": [
                False,
                "Raw view keeps the output as the raw markup for view mode - Default False",
            ],
        }

        super().__init__(*args, **kwargs)

        self.configured = False

    def extendMarkdown(self, md, md_globals):
        """Register the extension."""

        self.md = md
        md.registerExtension(self)
        self.critic_stash = CriticStash(CRITIC_KEY)
        post = CriticsPostprocessor(self.critic_stash)
        critic = CriticViewPreprocessor(self.critic_stash)
        critic.config = self.getConfigs()
        md.preprocessors.add("critic", critic, ">normalize_whitespace")
        md.postprocessors.add("critic-post", post, ">raw_html")

    def reset(self):
        """
        Try and make sure critic is handled first after "normalize_whitespace".

        Wait to until after all extensions have been loaded
        so we can be as sure as we can that this is the first
        thing run after "normalize_whitespace"
        """

        if not self.configured:
            self.configured = True
            self.md.preprocessors.link("critic", ">normalize_whitespace")
            self.md.postprocessors.link("critic-post", ">raw_html")
        self.critic_stash.clear()


def makeExtension(*args, **kwargs):
    """Return extension."""

    return CriticExtension(*args, **kwargs)
