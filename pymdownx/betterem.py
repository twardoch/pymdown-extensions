"""
Better Emphasis.

pymdownx.betterem
Add inteligent handling of to em and strong notations

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

from markdown import Extension
from markdown.inlinepatterns import DoubleTagPattern, SimpleTagPattern

SMART_UNDER_CONTENT = r"((?:[^_]|_(?=\w|\s)|(?<=\s)_+?(?=\s))+?_*?)"
SMART_STAR_CONTENT = r"((?:[^\*]|\*(?=[^\W_]|\*|\s)|(?<=\s)\*+?(?=\s))+?\**?)"
SMART_UNDER_MIXED_CONTENT = r"((?:[^_]|_(?=\w)|(?<=\s)_+?(?=\s))+?_*)"
SMART_STAR_MIXED_CONTENT = r"((?:[^\*]|\*(?=[^\W_]|\*)|(?<=\s)\*+?(?=\s))+?\**)"
UNDER_CONTENT = r"(_|(?:(?<=\s)_|[^_])+?)"
UNDER_CONTENT2 = r"((?:[^_]|(?<!_)_(?=\w))+?)"
STAR_CONTENT = r"(\*|(?:(?<=\s)\*|[^\*])+?)"
STAR_CONTENT2 = r"((?:[^\*]|(?<!\*)\*(?=[^\W_]|\*))+?)"

# ***strong,em***
STAR_STRONG_EM = r"(\*{3})(?!\s)(\*{1,2}|[^\*]+?)(?<!\s)\2"
# ___strong,em___
UNDER_STRONG_EM = r"(_{3})(?!\s)(_{1,2}|[^_]+?)(?<!\s)\2"
# ***strong,em*strong**
STAR_STRONG_EM2 = r"(\*{{3}})(?![\s\*]){}(?<!\s)\*{}(?<!\s)\*{{2}}".format(
    STAR_CONTENT, STAR_CONTENT2
)
# ___strong,em_strong__
UNDER_STRONG_EM2 = r"(_{{3}})(?![\s_]){}(?<!\s)_{}(?<!\s)_{{2}}".format(
    UNDER_CONTENT, UNDER_CONTENT2
)
# ***em,strong**em*
STAR_EM_STRONG = r"(\*{{3}})(?![\s\*]){}(?<!\s)\*{{2}}{}(?<!\s)\*".format(
    STAR_CONTENT2, STAR_CONTENT
)
# ___em,strong__em_
UNDER_EM_STRONG = r"(_{{3}})(?![\s_]){}(?<!\s)_{{2}}{}(?<!\s)_".format(
    UNDER_CONTENT2, UNDER_CONTENT
)
# **strong**
STAR_STRONG = r"(\*{2})(?!\s)%s(?<!\s)\2" % STAR_CONTENT2
# __strong__
UNDER_STRONG = r"(_{2})(?!\s)%s(?<!\s)\2" % UNDER_CONTENT2
# *emphasis*
STAR_EM = r"(\*)(?!\s)%s(?<!\s)\2" % STAR_CONTENT
# _emphasis_
UNDER_EM = r"(_)(?!\s)%s(?<!\s)\2" % UNDER_CONTENT

# Smart rules for when "smart underscore" is enabled
# SMART: ___strong,em___
SMART_UNDER_STRONG_EM = r"(?<!\w)(_{3})(?![\s_])%s(?<!\s)\2(?!\w)" % SMART_UNDER_CONTENT
# ___strong,em_ strong__
SMART_UNDER_STRONG_EM2 = (
    r"(?<!\w)(_{{3}})(?![\s_]){}(?<!\s)_(?!\w){}(?<!\s)_{{2}}(?!\w)".format(
        SMART_UNDER_MIXED_CONTENT, SMART_UNDER_CONTENT
    )
)
# ___em,strong__ em_
SMART_UNDER_EM_STRONG = (
    r"(?<!\w)(_{{3}})(?![\s_]){}(?<!\s)_{{2}}(?!\w){}(?<!\s)_(?!\w)".format(
        SMART_UNDER_MIXED_CONTENT, SMART_UNDER_CONTENT
    )
)
# __strong__
SMART_UNDER_STRONG = r"(?<!\w)(_{2})(?![\s_])%s(?<!\s)\2(?!\w)" % SMART_UNDER_CONTENT
# SMART _em_
SMART_UNDER_EM = r"(?<!\w)(_)(?![\s_])%s(?<!\s)\2(?!\w)" % SMART_UNDER_CONTENT

# Smart rules for when "smart asterisk" is enabled
# SMART: ***strong,em***
SMART_STAR_STRONG_EM = (
    r"(?:(?<=_)|(?<![\w\*]))(\*{3})(?![\s\*])%s(?<!\s)\2(?:(?=_)|(?![\w\*]))"
    % SMART_STAR_CONTENT
)
# ***strong,em* strong**
SMART_STAR_STRONG_EM2 = r"(?:(?<=_)|(?<![\w\*]))(\*{{3}})(?![\s\*]){}(?<!\s)\*(?:(?=_)|(?![\w\*])){}(?<!\s)\*{{2}}(?:(?=_)|(?![\w\*]))".format(
    SMART_STAR_MIXED_CONTENT, SMART_STAR_CONTENT
)
# ***em,strong** em*
SMART_STAR_EM_STRONG = r"(?:(?<=_)|(?<![\w\*]))(\*{{3}})(?![\s\*]){}(?<!\s)\*{{2}}(?:(?=_)|(?![\w\*])){}(?<!\s)\*(?:(?=_)|(?![\w\*]))".format(
    SMART_STAR_MIXED_CONTENT, SMART_STAR_CONTENT
)
# **strong**
SMART_STAR_STRONG = (
    r"(?:(?<=_)|(?<![\w\*]))(\*{2})(?![\s\*])%s(?<!\s)\2(?:(?=_)|(?![\w\*]))"
    % SMART_STAR_CONTENT
)
# SMART *em*
SMART_STAR_EM = (
    r"(?:(?<=_)|(?<![\w\*]))(\*)(?![\s\*])%s(?<!\s)\2(?:(?=_)|(?![\w\*]))"
    % SMART_STAR_CONTENT
)


class BetterEmExtension(Extension):
    """Add extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            "smart_enable": [
                "underscore",
                "Treat connected words intelligently - Default: underscore",
            ]
        }

        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Modify inline patterns."""

        # Not better yet, so let's make it better
        md.registerExtension(self)
        self.make_better(md)

    def make_better(self, md):
        """
        Configure all the pattern rules.

        This should be used instead of smart_strong package.
        pymdownx.extra should be used in place of makrdown.extensions.extra.
        """

        config = self.getConfigs()
        enabled = config["smart_enable"]
        if enabled:
            enable_all = enabled == "all"
            enable_under = enabled == "underscore" or enable_all
            enable_star = enabled == "asterisk" or enable_all

        star_strong_em = SMART_STAR_STRONG_EM if enable_star else STAR_STRONG_EM
        under_strong_em = SMART_UNDER_STRONG_EM if enable_under else UNDER_STRONG_EM
        star_em_strong = SMART_STAR_EM_STRONG if enable_star else STAR_EM_STRONG
        under_em_strong = SMART_UNDER_EM_STRONG if enable_under else UNDER_EM_STRONG
        star_strong_em2 = SMART_STAR_STRONG_EM2 if enable_star else STAR_STRONG_EM2
        under_strong_em2 = SMART_UNDER_STRONG_EM2 if enable_under else UNDER_STRONG_EM2
        star_strong = SMART_STAR_STRONG if enable_star else STAR_STRONG
        under_strong = SMART_UNDER_STRONG if enable_under else UNDER_STRONG
        star_emphasis = SMART_STAR_EM if enable_star else STAR_EM
        under_emphasis = SMART_UNDER_EM if enable_under else UNDER_EM

        md.inlinePatterns["strong_em"] = DoubleTagPattern(star_strong_em, "strong,em")
        md.inlinePatterns.add(
            "strong_em2", DoubleTagPattern(under_strong_em, "strong,em"), ">strong_em"
        )
        md.inlinePatterns.link("em_strong", ">strong_em2")
        md.inlinePatterns["em_strong"] = DoubleTagPattern(star_em_strong, "em,strong")
        md.inlinePatterns.add(
            "em_strong2", DoubleTagPattern(under_em_strong, "em,strong"), ">em_strong"
        )
        md.inlinePatterns.add(
            "strong_em3", DoubleTagPattern(star_strong_em2, "strong,em"), ">em_strong2"
        )
        md.inlinePatterns.add(
            "strong_em4", DoubleTagPattern(under_strong_em2, "strong,em"), ">strong_em3"
        )
        md.inlinePatterns["strong"] = SimpleTagPattern(star_strong, "strong")
        md.inlinePatterns.add(
            "strong2", SimpleTagPattern(under_strong, "strong"), ">strong"
        )
        md.inlinePatterns["emphasis"] = SimpleTagPattern(star_emphasis, "em")
        md.inlinePatterns["emphasis2"] = SimpleTagPattern(under_emphasis, "em")


def makeExtension(*args, **kwargs):
    """Return extension."""

    return BetterEmExtension(*args, **kwargs)
