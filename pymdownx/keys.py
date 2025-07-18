"""
Keys.

pymdownx.keys
Markdown extension for keystroke (user keyboard input) formatting.

It wraps the syntax `++key+key+key++` (for individual keystrokes with modifiers)
or `++"string"++` (for continuous keyboard input) into HTML `<kbd>` elements.

If a key is found in the extension's database, its `<kbd>` element gets a matching class.
Common synonyms are included, e.g. `++pg-up++` will match as `++page-up++`.

## Config

If `strict` is `True`, the entire series of keystrokes is wrapped into an outer`<kbd>` element, and then,
each keystroke is wrapped into a separate inner `<kbd>` element, which matches the HTML5 spec.
If `strict` is `False`, an outer `<span>` is used, which matches the practice on Github or StackOverflow.

The resulting `<kbd>` elements are separated by `separator` (`+` by default, can be `''` or something else).

If `camel_case` is `True`, `++PageUp++` will match the same as `++page-up++`.

The database can be extended or modified with the `key_map` dict.

## Examples

### Input

```markdown
Press ++Shift+Alt+PgUp++, type in ++"Hello"++ and press ++Enter++.
```

### Config 1

```yaml
  pymdownx.keys:
    camel_case: true
    strict: false
    separator: '+'
```

### Output 1

```html
<p>Press <span class="keys"><kbd class="key-shift">Shift</kbd><span>+</span><kbd
class="key-alt">Alt</kbd><span>+</span><kbd class="key-page-up">Page Up</kbd></span>, type in <span
class="keys"><kbd>Hello</kbd></span> and press <span class="keys"><kbd class="key-enter">Enter</kbd></span>.</p>
```

### Config 2

```yaml
  pymdownx.keys:
    camel_case: true
    strict: true
    separator: ''
```

### Output 2

```html
<p>Press <kbd class="keys"><kbd class="key-shift">Shift</kbd><kbd class="key-alt">Alt</kbd><kbd
class="key-page-up">Page Up</kbd></kbd>, type in <kbd class="keys"><kbd>Hello</kbd></kbd> and press <kbd
class="keys"><kbd class="key-enter">Enter</kbd></kbd>.</p>
```

Idea by Adam Twardoch and coded by Isaac Muse.

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

import re

from markdown import Extension
from markdown import util as md_util
from markdown.inlinepatterns import Pattern

from . import keymap_db as keymap
from . import util

RE_KBD = r"""(?x)
(?:
    # Escape
    (?<!\\)(?P<escapes>(?:\\{2})+)(?=\+)|
    # Key
    (?<!\\)\+{2}
    (
        (?:(?:[\w\-]+|"(?:\\.|[^"])+"|\'(?:\\.|[^\'])+\')\+)*?
        (?:[\w\-]+|"(?:\\.|[^"])+"|\'(?:\\.|[^\'])+\')
    )
    \+{2}
)
"""

ESCAPE_RE = re.compile(r"""(?<!\\)(?:\\\\)*\\(.)""")
UNESCAPED_PLUS = re.compile(r"""(?<!\\)(?:\\\\)*(\+)""")
ESCAPED_BSLASH = "{}{}{}".format(md_util.STX, ord("\\"), md_util.ETX)
DOUBLE_BSLASH = "\\\\"


class KeysPattern(Pattern):
    """Return kbd tag."""

    def __init__(self, pattern, config, md):
        """Initialize."""

        self.ksep = config["separator"]
        self.markdown = md
        self.strict = config["strict"]
        self.classes = config["class"].split(" ")
        self.html_parser = util.HTMLParser()
        self.map = self.merge(keymap.keymap, config["key_map"])
        self.aliases = keymap.aliases
        self.camel = config["camel_case"]
        super().__init__(pattern)

    def merge(self, x, y):
        """Given two dicts, merge them into a new dict."""

        z = x.copy()
        z.update(y)
        return z

    def normalize(self, key):
        """Normalize the value."""

        if not self.camel:
            return key

        norm_key = []
        last = ""
        for c in key:
            if c.isupper():
                if not last or last == "-":
                    norm_key.append(c.lower())
                else:
                    norm_key.extend(["-", c.lower()])
            else:
                norm_key.append(c)
            last = c
        return "".join(norm_key)

    def process_key(self, key):
        """Process key."""

        if key.startswith(('"', "'")):
            value = (
                None,
                self.html_parser.unescape(ESCAPE_RE.sub(r"\1", key[1:-1])).strip(),
            )
        else:
            norm_key = self.normalize(key)
            canonical_key = self.aliases.get(norm_key, norm_key)
            name = self.map.get(canonical_key, None)
            value = (canonical_key, name) if name else None
        return value

    def handleMatch(self, m):
        """Handle kbd pattern matches."""

        if m.group(2):
            return m.group("escapes").replace(DOUBLE_BSLASH, ESCAPED_BSLASH)
        content = [
            self.process_key(key)
            for key in UNESCAPED_PLUS.split(m.group(3))
            if key != "+"
        ]

        if None in content:
            return

        el = md_util.etree.Element(
            ("kbd" if self.strict else "span"),
            ({"class": " ".join(self.classes)} if self.classes else {}),
        )

        last = None
        for item_class, item_name in content:
            classes = []
            if item_class:
                classes.append("key-" + item_class)
            if last is not None and self.ksep:
                span = md_util.etree.SubElement(el, "span")
                span.text = md_util.AtomicString(self.ksep)
            attr = {}
            if classes:
                attr["class"] = " ".join(classes)
            kbd = md_util.etree.SubElement(el, "kbd", attr)
            kbd.text = md_util.AtomicString(item_name)
            last = kbd

        return el


class KeysExtension(Extension):
    """Add `keys`` extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            "separator": ["+", 'Provide a keyboard separator - Default: "+"'],
            "strict": [
                False,
                "Format keys and menus according to HTML5 spec - Default: False",
            ],
            "class": [
                "keys",
                'Provide class(es) for the kbd elements - Default: "keys"',
            ],
            "camel_case": [
                False,
                "Allow camelCase conversion for key names PgDn -> pg-dn - Default: False",
            ],
            "key_map": [
                {},
                "Additional keys to include or keys to override - Default: {}",
            ],
        }
        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add support for keys."""

        util.escape_chars(md, ["+"])
        md.inlinePatterns.add(
            "keys", KeysPattern(RE_KBD, self.getConfigs(), md), "<escape"
        )


def makeExtension(*args, **kwargs):
    """Return extension."""

    return KeysExtension(*args, **kwargs)
