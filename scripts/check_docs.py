#!/usr/bin/env python3
"""Check navigable CAPT-Bot documentation links, anchors and Markdown fences.

Checks source files without network or non-standard dependencies.
Historical design plans are preserved but are not part of this public-front-door gate.
"""
from __future__ import annotations

import collections
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

BACKTICK = chr(96)
LINK_RE = re.compile(r"\]\(([^)\n]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")
HTML_ANCHOR_RE = re.compile(r'<a\s+(?:id|name)="([^"]+)"', flags=re.I)


def pages(root: Path) -> list[Path]:
    candidates = [root / "README.md", root / "CONTRIBUTING.md"]
    candidates.extend(sorted((root / "docs").glob("*.md")))
    candidates.extend(sorted((root / "docs" / "audit").glob("*.md")))
    candidates.append(root / "docs" / "architecture" / "CAPT_BOT_R5_STAGE_B_SOURCE_ADMISSION.md")
    return [p for p in candidates if p.is_file()]


def slug(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace(BACKTICK, "").replace("*", "").replace("_", "").strip().lower()
    text = "".join(c for c in text if c.isalnum() or c.isspace() or c == "-")
    return re.sub(r"\s+", "-", text)


def visible_lines(text: str) -> tuple[list[str], list[int]]:
    output: list[str] = []
    unfinished: list[int] = []
    opening: tuple[str, int, int] | None = None
    for number, line in enumerate(text.splitlines(), 1):
        candidate = re.match(r"^\s{0,3}(" + BACKTICK + r"{3,}|~{3,})(.*)$", line)
        if candidate:
            marker = candidate.group(1)
            if opening is None:
                opening = marker[0], len(marker), number
                continue
            if marker[0] == opening[0] and len(marker) >= opening[1] and not candidate.group(2).strip():
                opening = None
                continue
        if opening is None:
            output.append(line)
    if opening:
        unfinished.append(opening[2])
    return output, unfinished


def anchors_for(text: str) -> set[str]:
    lines, _ = visible_lines(text)
    anchors: set[str] = set()
    seen: collections.Counter[str] = collections.Counter()
    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            name = slug(match.group(1))
            if name:
                count = seen[name]
                seen[name] += 1
                anchors.add(name if count == 0 else f"{name}-{count}")
        anchors.update(HTML_ANCHOR_RE.findall(line))
    return anchors


def check(root: Path) -> tuple[list[str], int, int]:
    root = root.resolve()
    docs = pages(root)
    anchor_map = {p.resolve(): anchors_for(p.read_text(encoding="utf-8")) for p in docs}
    problems: list[str] = []
    count = 0
    for file in docs:
        relative = file.relative_to(root)
        lines, unclosed = visible_lines(file.read_text(encoding="utf-8"))
        for start in unclosed:
            problems.append(f"{relative}:{start}: unclosed Markdown fence")
        for number, line in enumerate(lines, 1):
            for match in LINK_RE.finditer(line):
                target = match.group(1).strip().strip("<>")
                if target.startswith(("http://", "https://", "mailto:", "data:")):
                    continue
                target = unquote(target)
                count += 1
                path, _, fragment = target.partition("#")
                destination = (file.parent / path).resolve() if path else file.resolve()
                if destination != root and root not in destination.parents:
                    problems.append(f"{relative}:{number}: link escapes repository: {target}")
                elif not destination.is_file():
                    problems.append(f"{relative}:{number}: missing link destination: {target}")
                elif fragment and destination in anchor_map and fragment not in anchor_map[destination]:
                    problems.append(f"{relative}:{number}: missing anchor: {target}")
    return problems, len(docs), count


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    problems, scanned, links = check(root)
    for problem in problems:
        print("FAIL:", problem, file=sys.stderr)
    if problems:
        print(f"FAIL docs: {len(problems)} finding(s), {scanned} files, {links} local links")
        return 1
    print(f"PASS docs: {scanned} files, {links} local links, 0 broken destinations/anchors/fences")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
