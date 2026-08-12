"""Check that manuscript citation keys are present in the BibTeX file."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEX_PATH = ROOT / "paper" / "arxiv" / "main.tex"
BIB_PATH = ROOT / "paper" / "arxiv" / "references.bib"


def strip_tex_comments(text: str) -> str:
    return "\n".join(line.split("%", 1)[0] for line in text.splitlines())


def citation_keys(tex_text: str) -> set[str]:
    keys: set[str] = set()
    pattern = re.compile(r"\\cite[a-zA-Z*]*(?:\[[^\]]*\])*\{([^}]+)\}")
    for match in pattern.finditer(strip_tex_comments(tex_text)):
        for key in match.group(1).split(","):
            key = key.strip()
            if key:
                keys.add(key)
    return keys


def bib_keys(bib_text: str) -> set[str]:
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", bib_text))


def main() -> int:
    tex_keys = citation_keys(TEX_PATH.read_text(encoding="utf-8"))
    references = bib_keys(BIB_PATH.read_text(encoding="utf-8"))
    missing = sorted(tex_keys - references)
    unused = sorted(references - tex_keys)

    print(f"Found {len(tex_keys)} cited keys and {len(references)} BibTeX entries.")
    if missing:
        print("Missing BibTeX entries:")
        for key in missing:
            print(f"  - {key}")
    if unused:
        print("Unused BibTeX entries:")
        for key in unused:
            print(f"  - {key}")

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
