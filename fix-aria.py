#!/usr/bin/env python3
"""
Post-render script: remove the invalid role="menu" attribute that Quarto's
Bootstrap template places on the .navbar-toggler <button>.

A <button> has the implicit ARIA role "button". Adding role="menu" is
incorrect and causes a WAVE "Broken ARIA menu" error because a role="menu"
element must contain role="menuitem" children, which the toggler does not.

This runs as a Quarto post-render hook so the fix is baked into every
generated HTML file rather than relying on JavaScript timing.
"""
import re
import sys
from pathlib import Path

OUTPUT_DIR = Path("_site")

PATTERN = re.compile(
    r'(<button\b[^>]*class="[^"]*\bnavbar-toggler\b[^"]*"[^>]*)\s+role="menu"([^>]*>)',
    re.DOTALL,
)


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    new_text, count = PATTERN.subn(r"\1\2", text)
    if count:
        path.write_text(new_text, encoding="utf-8")
        print(f"Fixed {count} occurrence(s) in {path}", file=sys.stderr)
        return True
    return False


def main() -> None:
    if not OUTPUT_DIR.exists():
        print(f"Output directory {OUTPUT_DIR} not found; skipping.", file=sys.stderr)
        return
    for html_file in OUTPUT_DIR.rglob("*.html"):
        fix_file(html_file)


if __name__ == "__main__":
    main()
