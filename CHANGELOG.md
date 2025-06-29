# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-06-29

### Changed
- Significant refactoring of emoji database files (`emoji1_db.py`, `gemoji_db.py`, `twemoji_db.py`)
  - Reduced file sizes by approximately 50% (from ~17,221 deletions and 8,133 insertions)
  - Optimized database structure for better performance
- Code formatting improvements across all Python modules
- Updated code style to be more consistent with modern Python practices
- Refactored extension modules for better maintainability

### Technical Details
- All extension modules have been reformatted for consistency
- Import statements reorganized
- String formatting updated
- Function signatures improved
- Documentation strings enhanced

### Files Modified
- Core extension modules: arithmatex, b64, betterem, caret, critic, details, emoji, escapeall, extra, extrarawhtml, github, highlight, inlinehilite, keys, magiclink, mark, pathconverter, plainhtml, progressbar, slugs, smartsymbols, snippets, spoilers, superfences, tasklist, tilde
- Database files: emoji1_db, gemoji_db, keymap_db, twemoji_db
- Utility modules: util.py
- Test files: run_tests.py, test_syntax.py, test_targeted.py, spellcheck.py
- Tools: gen_critic_doc.py, gen_emoji.py, gen_emoji1.py, gen_gemoji.py, gen_twemoji.py
- Setup files: setup.py

## [3.5.0] - 2017-06-13

Released June 13, 2017

- **NEW**: Add new slugs to preserve case (https://github.com/facelessuser/pymdown-extensions/pull/103).
- **NEW**: Add new GFM specific slug (both percent encoded and normal) that only lowercases ASCII chars just like GFM does (https://github.com/facelessuser/pymdown-extensions/issues/101).
- **FIX**: PathConverter should not try and convert obscured email address (with HTML entities) (https://github.com/facelessuser/pymdown-extensions/issues/100).
- **FIX**: Don't normalize Unicode in slugs with `NFKD`, use `NFC` instead (https://github.com/facelessuser/pymdown-extensions/issues/98).
- **FIX**: Don't let EscapeAll escape CriticMarkup placeholders. EscapeAll will no longer escape `STX` and `ETX`; they will just pass through (https://github.com/facelessuser/pymdown-extensions/issues/95).
- **FIX**: Replace CriticMarkup placeholders after replacing raw HTML placeholders (https://github.com/facelessuser/pymdown-extensions/issues/95).

*Note: Earlier changelog entries can be found in docs/src/markdown/changelog.md*