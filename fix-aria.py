#!/usr/bin/env python3
"""
Post-render script: remove the invalid role="menu" attribute that Quarto's
Bootstrap template places on the .navbar-toggler <button>.

A <button> has the implicit ARIA role "button". Adding role="menu" is
incorrect and causes a WAVE "Broken ARIA menu" error because a role="menu"
element must contain role="menuitem" children, which the toggler does not.

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


def _fix_button_tag(match: re.Match) -> str:
    """Remove role="menu" from a button tag that has the navbar-toggler class."""
    tag = match.group(0)
    if _TOGGLER_CLASS.search(tag):
        tag = _ROLE_MENU.sub("", tag)
    return tag


def fix_file(path: Path) -> bool:
    """Strip ``role="menu"`` from navbar-toggler buttons in an HTML file.

    Args:
        path: Path to the HTML file to process.

    Returns:
        ``True`` if the file was modified and written back, ``False`` if no
        changes were needed or if an I/O error prevented processing.
    """
    try:
        text = path.read_text(encoding="utf-8")
        new_text = _BUTTON_TAG.sub(_fix_button_tag, text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            print(f"Fixed role=menu in {path}", file=sys.stderr)
            return True
    except (OSError, PermissionError) as exc:
        print(f"Warning: could not process {path}: {exc}", file=sys.stderr)
    return False


def main() -> None:
    output_dir = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.environ.get("QUARTO_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    )
    output_path = Path(output_dir)
    if not output_path.exists():
        print(f"Output directory {output_path} not found; skipping.", file=sys.stderr)
        return
    for html_file in output_path.rglob("*.html"):
        fix_file(html_file)


if __name__ == "__main__":
    main()
