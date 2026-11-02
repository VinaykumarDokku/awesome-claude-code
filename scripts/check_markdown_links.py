"""Check whether local Markdown links point to existing files."""

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK_PATTERN = re.compile(r'!?\[[^\]]*\]\(([^)]+)\)')


def check_links(markdown_file):
    content = markdown_file.read_text(encoding="utf-8")
    broken_links = []

    for raw_target in LINK_PATTERN.findall(content):
        target = raw_target.strip().split(" ", 1)[0].strip("<>")

        if not target or target.startswith("#"):
            continue

        parsed = urlsplit(target)

        if parsed.scheme or parsed.netloc or target.startswith("//"):
            continue

        path = unquote(parsed.path)

        if not path:
            continue

        if path.startswith("/"):
            destination = Path.cwd() / path.lstrip("/")
        else:
            destination = markdown_file.parent / path

        if not destination.exists():
            broken_links.append(target)

    return broken_links


def main():
    files = sorted(Path(".").rglob("*.md"))
    files = [
        file for file in files
        if ".git" not in file.parts
        and "node_modules" not in file.parts
    ]

    if not files:
        print("No Markdown files found.")
        return 0

    total_broken = 0

    for file in files:
        broken = check_links(file)

        for link in broken:
            print(f"{file}: Broken local link: {link}")

        total_broken += len(broken)

    print(f"Checked {len(files)} Markdown files.")
    print(f"Broken local links: {total_broken}")

    return 1 if total_broken else 0


if __name__ == "__main__":
    sys.exit(main())
