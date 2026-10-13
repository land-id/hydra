#!/usr/bin/env python3
"""Adds a "Modified by Land id" notice to each file given that lacks one.

Apache 2.0 asks that modified files carry a prominent notice that they were
changed. land-id-modified-notice.yml runs this on the files a PR modifies.

The notice goes under the file's license header (the "SPDX-License-Identifier"
line), or at the top if it has none, after any shebang. Files whose type has no
comment syntax (JSON, go.sum, ...) are skipped; LAND_ID.md covers those.

Usage: add-modified-notice.py FILE...
Prints each file it changed.
"""

import os
import sys

MARKER = "Modified by Land id"

# Files Land id wrote rather than modified.
OURS = {
    "LAND_ID.md",
    ".github/scripts/add-modified-notice.py",
}
OURS_PREFIX = ".github/workflows/land-id-"
TEXT = MARKER + ". See LAND_ID.md."

# Line-comment prefix by file name or extension.
BY_NAME = {
    "go.mod": "//",
    "Makefile": "#",
    "Dockerfile": "#",
}
BY_EXT = {
    ".go": "//",
    ".js": "//",
    ".jsx": "//",
    ".ts": "//",
    ".tsx": "//",
    ".proto": "//",
    ".yml": "#",
    ".yaml": "#",
    ".sh": "#",
    ".py": "#",
    ".toml": "#",
    ".sql": "--",
}
# Block-comment wrappers for types without a line comment.
BLOCK_BY_EXT = {
    ".md": ("<!-- ", " -->"),
    ".html": ("<!-- ", " -->"),
    ".css": ("/* ", " */"),
}


def notice_for(path):
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1]
    prefix = BY_NAME.get(name) or BY_EXT.get(ext)
    if prefix is None and name.startswith("Dockerfile"):
        prefix = "#"
    if prefix is not None:
        return prefix + " " + TEXT + "\n", prefix
    if ext in BLOCK_BY_EXT:
        start, end = BLOCK_BY_EXT[ext]
        return start + TEXT + end + "\n", None
    return None, None


def add_notice(path):
    if path in OURS or path.startswith(OURS_PREFIX):
        return False

    notice, prefix = notice_for(path)
    if notice is None:
        return False

    with open(path, encoding="utf-8") as f:
        content = f.read()
    if MARKER in content:
        return False

    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if "SPDX-License-Identifier" in line:
            # Continue the header's comment block so the notice reads as part
            # of it, e.g. "// SPDX...\n//\n// Modified by Land id...".
            sep = prefix + "\n" if prefix else ""
            lines[i + 1:i + 1] = [sep, notice]
            break
    else:
        at = 1 if lines and lines[0].startswith("#!") else 0
        # A blank line after the notice keeps it from becoming a Go package
        # doc comment or merging with whatever comment follows.
        lines[at:at] = [notice, "\n"]

    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(lines))
    return True


def main(paths):
    for path in paths:
        if os.path.isfile(path) and add_notice(path):
            print(path)


if __name__ == "__main__":
    main(sys.argv[1:])
