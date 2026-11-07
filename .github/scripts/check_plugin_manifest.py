"""Check that the Claude plugin manifest stays in sync with the skills.

- .claude-plugin/plugin.json must be valid JSON with a kebab-case "name".
- Its "version" must match metadata.version in every SKILL.md, so the
  claude.ai plugin ZIP and the .skill file carry the same version.

Usage: python3 check_plugin_manifest.py .claude-plugin/plugin.json skills/*/SKILL.md
"""

import json
import re
import sys
from pathlib import Path

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VERSION_LINE = re.compile(r'^  version: "(.*)"$', re.MULTILINE)


def main(manifest_path: str, skill_paths: list[str]) -> int:
    failed = False
    manifest_file = Path(manifest_path)
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"::error file={manifest_file}::cannot read plugin.json: {error}")
        return 1

    name = manifest.get("name", "")
    if not NAME_PATTERN.match(name):
        print(f"::error file={manifest_file}::'name' must be kebab-case, got {name!r}")
        failed = True

    version = manifest.get("version")
    if not version:
        print(f"::error file={manifest_file}::'version' is missing")
        failed = True

    for skill_path in skill_paths:
        path = Path(skill_path)
        match = VERSION_LINE.search(path.read_text(encoding="utf-8"))
        skill_version = match.group(1) if match else None
        if skill_version != version:
            print(
                f"::error file={path}::metadata.version ({skill_version}) does not match "
                f"plugin.json version ({version})"
            )
            failed = True

    print(f"checked {manifest_file}: name={name}, version={version}")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2:]))
