"""
Emoji.

pymdownx.emoji
Emoji extension for emojione or Github's gemoji.

MIT license.

Copyright (c) 2016 - 2017 Isaac Muse <isaacmuse@gmail.com>

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

import warnings

from markdown import Extension
from markdown import util as md_util
from markdown.inlinepatterns import Pattern

from . import util
from .util import PymdownxDeprecationWarning

RE_EMOJI = r"(:[+\-\w]+:)"
SUPPORTED_INDEXES = ("emojione", "gemoji", "twemoji")
UNICODE_VARIATION_SELECTOR_16 = "fe0f"
EMOJIONE_SVG_CDN = "https://cdn.jsdelivr.net/emojione/assets/svg/"
EMOJIONE_PNG_CDN = "https://cdn.jsdelivr.net/emojione/assets/3.0/png/64/"
TWEMOJI_SVG_CDN = "https://twemoji.maxcdn.com/2/svg/"
TWEMOJI_PNG_CDN = "https://twemoji.maxcdn.com/2/72x72/"
GITHUB_UNICODE_CDN = "https://assets-cdn.github.com/images/icons/emoji/unicode/"
GITHUB_CDN = "https://assets-cdn.github.com/images/icons/emoji/"
NO_TITLE = "none"
LONG_TITLE = "long"
SHORT_TITLE = "short"
VALID_TITLE = (LONG_TITLE, SHORT_TITLE, NO_TITLE)
UNICODE_ENTITY = "html_entity"
UNICODE_ALT = ("unicode", UNICODE_ENTITY)
LEGACY_ARG_COUNT = 8


def add_attriubtes(options, attributes):
    """Add aditional attributes from options."""

    attr = options.get("attributes", {})
    if attr:
        for k, v in attr.items():
            attributes[k] = v


def emojione():
    """The EmojiOne index."""

    from . import emoji1_db as emoji_map

    return {
        "name": emoji_map.name,
        "emoji": emoji_map.emoji,
        "aliases": emoji_map.aliases,
    }


def gemoji():
    """The Gemoji index."""

    from . import gemoji_db as emoji_map

    return {
        "name": emoji_map.name,
        "emoji": emoji_map.emoji,
        "aliases": emoji_map.aliases,
    }


def twemoji():
    """The Twemoji index."""

    from . import twemoji_db as emoji_map

    return {
        "name": emoji_map.name,
        "emoji": emoji_map.emoji,
        "aliases": emoji_map.aliases,
    }


###################
# Converters
###################
def to_png(index, shortname, alias, uc, alt, title, category, options, md):
    """Return png element."""

    if index == "gemoji":
        def_image_path = GITHUB_UNICODE_CDN
        def_non_std_image_path = GITHUB_CDN
    elif index == "twemoji":
        def_image_path = TWEMOJI_PNG_CDN
        def_image_path = TWEMOJI_PNG_CDN
    else:
        def_image_path = EMOJIONE_PNG_CDN
        def_non_std_image_path = EMOJIONE_PNG_CDN

    is_unicode = uc is not None
    classes = options.get("classes", index)

    # In genral we can use the alias, but github specific images don't have one for each alias.
    # We can tell we have a github specific if there is no Unicode value.
    if is_unicode:
        image_path = options.get("image_path", def_image_path)
    else:
        image_path = options.get("non_standard_image_path", def_non_std_image_path)

    src = f"{image_path}{uc if is_unicode else shortname[1:-1]}.png"

    attributes = {"class": classes, "alt": alt, "src": src}

    if title:
        attributes["title"] = title

    add_attriubtes(options, attributes)

    return md_util.etree.Element("img", attributes)


def to_svg(index, shortname, alias, uc, alt, title, category, options, md):
    """Return svg element."""

    if index == "twemoji":
        svg_path = TWEMOJI_SVG_CDN
    else:
        svg_path = EMOJIONE_SVG_CDN

    attributes = {
        "class": options.get("classes", index),
        "alt": alt,
        "src": "{}{}.svg".format(options.get("image_path", svg_path), uc),
    }

    if title:
        attributes["title"] = title

    add_attriubtes(options, attributes)

    return md_util.etree.Element("img", attributes)


def to_png_sprite(index, shortname, alias, uc, alt, title, category, options, md):
    """Return png sprite element."""

    attributes = {
        "class": "%(class)s-%(size)s-%(category)s _%(unicode)s"
        % {
            "class": options.get("classes", index),
            "size": options.get("size", "64"),
            "category": (category if category else ""),
            "unicode": uc,
        }
    }

    if title:
        attributes["title"] = title

    add_attriubtes(options, attributes)

    el = md_util.etree.Element("span", attributes)
    el.text = md_util.AtomicString(alt)

    return el


def to_svg_sprite(index, shortname, alias, uc, alt, title, category, options, md):
    """
    Return svg sprite element.

    <svg class="%(classes)s"><description>%(alt)s</description>
    <use xlink:href="%(sprite)s#emoji-%(unicode)s"></use></svg>
    """

    xlink_href = "{}#emoji-{}".format(
        options.get("image_path", "./../assets/sprites/emojione.sprites.svg"), uc
    )
    svg = md_util.etree.Element("svg", {"class": options.get("classes", index)})
    desc = md_util.etree.SubElement(svg, "description")
    desc.text = md_util.AtomicString(alt)
    md_util.etree.SubElement(svg, "use", {"xlink:href": xlink_href})

    return svg


def to_awesome(index, shortname, alias, uc, alt, title, category, options, md):
    """
    Return "awesome style element for "font-awesome" format.

    See: https://github.com/Ranks/emojione/tree/master/lib/emojione-awesome.
    """

    classes = "{}-{}".format(options.get("classes", "e1a"), shortname[1:-1])
    attributes = {"class": classes}
    add_attriubtes(options, attributes)
    return md_util.etree.Element("i", attributes)


def to_alt(index, shortname, alias, uc, alt, title, category, options, md):
    """Return html entities."""

    return md.htmlStash.store(alt, safe=True)


###################
# Classes
###################
class EmojiPattern(Pattern):
    """Return element of type `tag` with a text attribute of group(3) of a Pattern."""

    def __init__(self, pattern, config, md):
        """Initialize."""

        title = config["title"]
        alt = config["alt"]

        self._set_index(config["emoji_index"])
        self.markdown = md
        self.unicode_alt = alt in UNICODE_ALT
        self.encoded_alt = alt == UNICODE_ENTITY
        self.remove_var_sel = config["remove_variation_selector"]
        self.title = title if title in VALID_TITLE else NO_TITLE
        self.generator = config["emoji_generator"]
        self.options = config["options"]
        Pattern.__init__(self, pattern)

    def _set_index(self, index):
        """Set the index."""

        self.emoji_index = index()

    def _remove_variation_selector(self, value):
        """Remove variation selectors."""

        return value.replace("-" + UNICODE_VARIATION_SELECTOR_16, "")

    def _get_unicode_char(self, value):
        """Get the Unicode char."""

        return "".join([util.get_char(int(c, 16)) for c in value.split("-")])

    def _get_unicode(self, emoji):
        """
        Get Unicode and Unicode alt.

        Unicode: This is the stripped down form of the Unicode, no joining chars and no variation chars.
            Unicode code points are not always valid.  If this is present and there is no 'unicode_alt',
            Unicode code points can be counted on as valid.  For the most part, the returned `uc` should
            be used to reference image files, or create classes, but for inserting actual Unicode, 'uc_alt'
            should be used.

        Unicode Alt: When present, this will always be valid Unicode points.  This contains not just the
            needed characters to identify the Unicode emoji, but the formatting as well. Joining characters
            and variation characters will be present. If you don't want variation chars, enable the global
            'remove_variation_selector' option.

        If using gemoji, it is possible you will get no Unicode and no Unicode alt.  This occurs with emoji
        like :octocat:.  :octocat: is not a real emoji and has no Unicode code points, but it is provided by
        gememoji as an emoji anyways.
        """

        uc = emoji.get("unicode")
        uc_alt = emoji.get("unicode_alt", uc)
        if uc_alt and self.remove_var_sel:
            uc_alt = self._remove_variation_selector(uc_alt)

        return uc, uc_alt

    def _get_title(self, shortname, emoji):
        """Get the title."""

        if self.title == LONG_TITLE:
            title = emoji["name"]
        elif self.title == SHORT_TITLE:
            title = shortname
        else:
            title = None
        return title

    def _get_alt(self, shortname, uc_alt):
        """Get alt form."""

        if uc_alt is None or not self.unicode_alt:
            alt = shortname
        else:
            alt = self._get_unicode_char(uc_alt)
            if self.encoded_alt:
                alt = "".join(
                    [
                        md_util.AMP_SUBSTITUTE + ("#x%04x;" % util.get_ord(point))
                        for point in util.get_code_points(alt)
                    ]
                )
        return alt

    def _get_category(self, emoji):
        """Get the category."""

        return emoji.get("category")

    def handleMatch(self, m):
        """Hanlde emoji pattern matches."""

        el = m.group(2)

        shortname = self.emoji_index["aliases"].get(el, el)
        alias = None if shortname == el else el
        emoji = self.emoji_index["emoji"].get(shortname, None)
        if emoji:
            uc, uc_alt = self._get_unicode(emoji)
            title = self._get_title(el, emoji)
            alt = self._get_alt(el, uc_alt)
            category = self._get_category(emoji)
            el = self.generator(
                self.emoji_index["name"],
                shortname,
                alias,
                uc,
                alt,
                title,
                category,
                self.options,
                self.markdown,
            )

        return el


class EmojiExtension(Extension):
    """Add emoji extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            "emoji_index": [
                emojione,
                "Function that returns the desired emoji index. - Default: 'pymdownx.emoji.emojione'",
            ],
            "emoji_generator": [
                to_png,
                "Emoji generator method. - Default: pymdownx.emoji.to_png",
            ],
            "title": [
                "short",
                "What title to use on images. You can use 'long' which shows the long name, "
                "'short' which shows the shortname (:short:), or 'none' which shows no title. "
                "- Default: 'short'",
            ],
            "alt": [
                "unicode",
                "Control alt form. 'short' sets alt to the shortname (:short:), 'uniocde' sets "
                "alt to the raw Unicode value, and 'html_entity' sets alt to the HTML entity. "
                "- Default: 'unicode'",
            ],
            "remove_variation_selector": [
                False,
                "Remove variation selector 16 from unicode. - Default: False",
            ],
            "options": [
                {},
                "Emoji options see documentation for options for github and emojione.",
            ],
        }
        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add support for emojis."""

        config = self.getConfigs()

        # To avoid having to do a major release, we'll support the old format until the next major release.
        if (
            util.get_arg_count(config["emoji_generator"]) == LEGACY_ARG_COUNT
        ):  # pragma: no coverage
            legacy_gen = config["emoji_generator"]
            config["emoji_generator"] = (
                lambda index,
                shortname,
                alias,
                uc,
                alt,
                title,
                category,
                options,
                md,
                legacy_gen=legacy_gen: legacy_gen(
                    index, shortname, alias, uc, alt, title, options, md
                )
            )
            warnings.warn(
                "'Emoji generators' now take 9 arguments. The 8 argument format is \n"
                "\ndeprecated and will be removed in the future. Please update your\n"
                "\ngenerator to the new format to avoid complications in the future.",
                PymdownxDeprecationWarning,
            )

        util.escape_chars(md, [":"])

        emj = EmojiPattern(RE_EMOJI, config, md)
        md.inlinePatterns.add("emoji", emj, "<not_strong")


###################
# Make Available
###################
def makeExtension(*args, **kwargs):
    """Return extension."""

    return EmojiExtension(*args, **kwargs)
