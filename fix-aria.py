#!/usr/bin/env python3
"""
Post-render script: apply navbar accessibility fixes to Quarto's generated HTML.

This script currently:
- removes the invalid role="menu" attribute that Quarto places on the
  .navbar-toggler <button>
- labels the primary and secondary navigation lists
- upgrades dropdown toggles with button semantics and menu relationships
- hides decorative Bootstrap icons from assistive technologies

This runs as a Quarto post-render hook so the fix is baked into every
generated HTML file rather than relying on JavaScript timing.

Usage:
    python3 fix-aria.py [output_dir]

The output directory defaults to "_site" (Quarto's default) but can be
overridden via the first positional argument or the QUARTO_OUTPUT_DIR
environment variable.
"""
import os
import re
import sys
from pathlib import Path

DEFAULT_OUTPUT_DIR = "_site"

# Match any complete <button ...> opening tag, correctly skipping over
# quoted attribute values that may themselves contain ">".
_BUTTON_TAG = re.compile(
    r"""<button\b(?:[^>"']|"[^"]*"|'[^']*')*>""",
    re.DOTALL,
)
# Detect navbar-toggler as an exact CSS class (space- or quote-delimited).
# Uses separate alternations for single- and double-quoted class attributes
# so an opposite-quote character inside the value doesn't break the match.
_TOGGLER_CLASS = re.compile(
    r"""class="(?:[^"]* )?navbar-toggler(?= |")|"""
    r"""class='(?:[^']* )?navbar-toggler(?= |')"""
)
# The role="menu" (or role='menu') attribute to strip (with surrounding whitespace).
_ROLE_MENU = re.compile(r"""\s+role=["']menu["']""")
_NAV_LIST = re.compile(
    r"""<ul class="navbar-nav navbar-nav-scroll (?P<group>me-auto|ms-auto)"(?P<attrs>[^>]*)>"""
)
_DROPDOWN_TOGGLE = re.compile(
    r"""<a\b(?P<attrs>[^>]*)class="(?P<class_attr>[^"]*\bnav-link\b[^"]*\bdropdown-toggle\b[^"]*)"(?P<rest>[^>]*)>""",
    re.DOTALL,
)
_DROPDOWN_MENU = re.compile(
    r"""<ul class="(?P<class_attr>[^"]*\bdropdown-menu\b[^"]*)"(?P<attrs>[^>]*)\saria-labelledby="(?P<label>[^"]+)"(?P<tail>[^>]*)>""",
    re.DOTALL,
)
_BOOTSTRAP_ICON_ROLE = re.compile(r"""(<i class="bi [^"]*")\s+role="img"([^>]*>)""")


def _fix_button_tag(match: re.Match) -> str:
    """Remove role="menu" from a button tag that has the navbar-toggler class."""
    tag = match.group(0)
    if _TOGGLER_CLASS.search(tag):
        tag = _ROLE_MENU.sub("", tag)
    return tag


def _label_nav_list(match: re.Match) -> str:
    """Add descriptive labels to the primary and utility nav lists."""
    group = match.group("group")
    attrs = match.group("attrs")
    if "aria-label=" in attrs:
        return match.group(0)
    label = "Primary navigation" if group == "me-auto" else "Secondary navigation"
    return f'<ul class="navbar-nav navbar-nav-scroll {group}"{attrs} aria-label="{label}">'


def _fix_dropdown_toggle(match: re.Match) -> str:
    """Give dropdown toggles button semantics and explicit menu relationships."""
    tag = match.group(0)
    if 'role="' not in tag and "role='" not in tag:
        tag = tag[:-1] + ' role="button">'
    else:
        tag = re.sub(r"""\srole=["']link["']""", ' role="button"', tag, count=1)
    if 'aria-haspopup="' not in tag and "aria-haspopup='" not in tag:
        tag = tag[:-1] + ' aria-haspopup="true">'
    id_match = re.search(r"""\sid=["']([^"']+)["']""", tag)
    if id_match and 'aria-controls="' not in tag and "aria-controls='" not in tag:
        tag = tag[:-1] + f' aria-controls="{id_match.group(1)}-menu">'
    return tag


def _fix_dropdown_menu(match: re.Match) -> str:
    """Assign a stable menu id derived from the controlling dropdown toggle."""
    tag = match.group(0)
    if ' id="' in tag or " id='" in tag:
        return tag
    label = match.group("label")
    return tag[:-1] + f' id="{label}-menu">'


def fix_file(path: Path) -> bool:
    """Strip ``role="menu"`` from navbar-toggler buttons in an HTML file.

    Args:
        path: Path to the HTML file to process.

    Returns:
        ``True`` if the file was modified and written back, ``False`` if no
        changes were needed.

    Raises:
        OSError: If the file cannot be read or written.
    """
    text = path.read_text(encoding="utf-8")
    new_text = _BUTTON_TAG.sub(_fix_button_tag, text)
    new_text = _NAV_LIST.sub(_label_nav_list, new_text)
    new_text = _DROPDOWN_TOGGLE.sub(_fix_dropdown_toggle, new_text)
    new_text = _DROPDOWN_MENU.sub(_fix_dropdown_menu, new_text)
    new_text = _BOOTSTRAP_ICON_ROLE.sub(r"\1 aria-hidden=\"true\"\2", new_text)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        print(f"Applied navbar accessibility fixes to {path}", file=sys.stderr)
        return True
    return False


def main() -> int:
    """Process all HTML files in the output directory and strip role=menu.

    Returns:
        0 on success, 1 if any file could not be processed due to I/O errors.
    """
    output_dir = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.environ.get("QUARTO_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    )
    output_path = Path(output_dir)
    if not output_path.exists():
        print(f"Output directory {output_path} not found; skipping.", file=sys.stderr)
        return 0
    errors = 0
    for html_file in output_path.rglob("*.html"):
        try:
            fix_file(html_file)
        except OSError as exc:
            print(f"Warning: could not process {html_file}: {exc}", file=sys.stderr)
            errors += 1
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
