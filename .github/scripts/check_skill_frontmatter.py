"""Check SKILL.md constraints that the Agent Skills reference validator does not cover.

- name and description must not contain angle brackets (Claude rejects XML-like text).
- SKILL.md should stay under 500 lines (warning only).

Usage: python3 check_skill_frontmatter.py skills/*/SKILL.md
"""

import sys
from pathlib import Path

MAX_LINES = 500
CHECKED_KEYS = ("name", "description")


def frontmatter_values(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    values: dict[str, str] = {}
    current = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line and not line[0].isspace() and ":" in line:
            key, _, value = line.partition(":")
            current = key.strip()
            value = value.strip()
            # Drop YAML block scalar indicators such as ">" or "|-".
            values[current] = "" if value[:1] in (">", "|") else value
        elif current is not None and line.strip():
            values[current] = (values[current] + " " + line.strip()).strip()
    return values


def main(paths: list[str]) -> int:
    failed = False
    for path_str in paths:
        path = Path(path_str)
        text = path.read_text(encoding="utf-8")
        values = frontmatter_values(text)
        if not values:
            print(f"::error file={path}::SKILL.md has no YAML frontmatter")
            failed = True
            continue
        for key in CHECKED_KEYS:
            if "<" in values.get(key, "") or ">" in values.get(key, ""):
                print(f"::error file={path}::'{key}' must not contain angle brackets (< or >)")
                failed = True
        line_count = len(text.splitlines())
        if line_count > MAX_LINES:
            print(f"::warning file={path}::SKILL.md has {line_count} lines; keep it under {MAX_LINES}")
        print(f"checked {path}: {line_count} lines")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
