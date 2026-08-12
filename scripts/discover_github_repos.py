"""Discover candidate GitHub repositories for the cooling-tools review queue.

The script uses the public GitHub Search API, compares results against links
already present in README.md and docs/candidate-repos.md, and writes a review
report. It does not auto-promote entries; maintainers should still apply the
repository review workflow before editing the main catalog.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MD = ROOT / "docs" / "generated" / "latest-github-discovery.md"
DEFAULT_CSV = ROOT / "data" / "discovery" / "latest-github-candidates.csv"

SEARCH_STREAMS = [
    ("data center cooling", "Primary cooling-specific mining stream"),
    ("datacenter cooling", "Variant spelling stream"),
    ("data center liquid cooling", "Liquid-cooling stream"),
    ("PUE data center", "Facility metric stream"),
    ("data center CDU liquid cooling", "Rack and CDU stream"),
    ("liquid cooled data center control", "Liquid-cooling controls stream"),
    ("data center thermal management github", "Thermal-management adjacent stream"),
    ("data center sustainability", "Sustainability, life-cycle, water, and carbon stream"),
    ("data center water cooling", "Water-aware cooling and scheduling stream"),
    ("data center life cycle assessment", "Life-cycle assessment stream"),
]

HIGH_SIGNAL_KEYWORDS = [
    "cooling",
    "liquid cooling",
    "thermal",
    "temperature",
    "cdu",
    "cold plate",
    "chiller",
    "hvac",
    "pue",
    "wue",
    "energy",
    "water",
    "carbon",
    "control",
    "reinforcement learning",
    "digital twin",
    "simulation",
    "modelica",
    "energyplus",
    "rack",
]

LOW_SIGNAL_PATTERNS = [
    "quora",
    "coding challenge",
    "algorithm challenge",
    "interview",
    "leetcode",
    "networking only",
]


@dataclass
class Candidate:
    full_name: str
    url: str
    description: str
    stream: str
    stars: int
    forks: int
    language: str
    updated_at: str
    pushed_at: str
    archived: bool
    topics: str
    tracked_status: str
    recommendation: str
    rationale: str


def now_date() -> str:
    return os.environ.get("DISCOVERY_DATE") or datetime.now(timezone.utc).date().isoformat()


def read_existing_links() -> set[str]:
    text_parts = []
    for path in [ROOT / "README.md", ROOT / "docs" / "candidate-repos.md"]:
        if path.exists():
            text_parts.append(path.read_text(encoding="utf-8"))
    text = "\n".join(text_parts).lower()
    links = set(re.findall(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", text))
    return {link.rstrip("/").lower() for link in links}


def github_request(url: str) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "data-center-cooling-research-tools-discovery",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API error {exc.code}: {body[:500]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub API connection failed: {exc.reason}") from exc


def classify(repo: dict, existing_links: set[str]) -> tuple[str, str, str]:
    url = repo["html_url"].rstrip("/").lower()
    tracked_status = "already tracked" if url in existing_links else "new to queue"
    text = " ".join(
        [
            repo.get("full_name") or "",
            repo.get("description") or "",
            " ".join(repo.get("topics") or []),
            repo.get("language") or "",
        ]
    ).lower()

    if repo.get("archived"):
        return tracked_status, "candidate", "Archived repository; keep only if the artifact remains scientifically useful."

    if any(pattern in text for pattern in LOW_SIGNAL_PATTERNS):
        return tracked_status, "exclude", "Likely search noise or challenge-style repository."

    high_signal_hits = [keyword for keyword in HIGH_SIGNAL_KEYWORDS if keyword in text]
    if tracked_status == "already tracked":
        return tracked_status, "already tracked", "Already appears in README.md or docs/candidate-repos.md."
    if len(high_signal_hits) >= 2:
        return tracked_status, "candidate", f"Cooling/energy relevance suggested by: {', '.join(high_signal_hits[:5])}."
    if high_signal_hits:
        return tracked_status, "review manually", f"One relevant signal found: {high_signal_hits[0]}."
    return tracked_status, "low priority", "No explicit cooling, energy, or thermal signal in API metadata."


def search_stream(query: str, per_page: int, existing_links: set[str]) -> list[Candidate]:
    encoded = urllib.parse.urlencode(
        {
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": str(per_page),
        }
    )
    data = github_request(f"https://api.github.com/search/repositories?{encoded}")
    candidates: list[Candidate] = []
    for repo in data.get("items", []):
        tracked_status, recommendation, rationale = classify(repo, existing_links)
        candidates.append(
            Candidate(
                full_name=repo.get("full_name") or "",
                url=repo.get("html_url") or "",
                description=repo.get("description") or "",
                stream=query,
                stars=int(repo.get("stargazers_count") or 0),
                forks=int(repo.get("forks_count") or 0),
                language=repo.get("language") or "",
                updated_at=repo.get("updated_at") or "",
                pushed_at=repo.get("pushed_at") or "",
                archived=bool(repo.get("archived")),
                topics="; ".join(repo.get("topics") or []),
                tracked_status=tracked_status,
                recommendation=recommendation,
                rationale=rationale,
            )
        )
    return candidates


def dedupe(candidates: list[Candidate]) -> list[Candidate]:
    seen: set[str] = set()
    unique: list[Candidate] = []
    for candidate in candidates:
        key = candidate.url.lower().rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def write_csv(candidates: list[Candidate], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(Candidate.__dataclass_fields__.keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for candidate in candidates:
            writer.writerow({field: getattr(candidate, field) for field in fields})


def markdown_table(candidates: list[Candidate]) -> list[str]:
    lines = [
        "| Repository | Stream | Updated | Stars | Recommendation | Rationale |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for candidate in candidates:
        updated = candidate.updated_at[:10]
        lines.append(
            f"| [{candidate.full_name}]({candidate.url}) | `{candidate.stream}` | {updated} | {candidate.stars} | {candidate.recommendation} | {candidate.rationale} |"
        )
    return lines


def write_markdown(candidates: list[Candidate], path: Path, discovered_on: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    new_candidates = [c for c in candidates if c.recommendation in {"candidate", "review manually"} and c.tracked_status == "new to queue"]
    tracked = [c for c in candidates if c.tracked_status == "already tracked"]
    low_priority = [c for c in candidates if c.recommendation in {"low priority", "exclude"} and c.tracked_status == "new to queue"]

    lines = [
        "# Latest GitHub Discovery Report",
        "",
        f"Generated on {discovered_on}. This report is a candidate-mining aid, not a citation list.",
        "",
        "## Search Streams",
        "",
        "| Query | Role |",
        "| --- | --- |",
    ]
    for query, role in SEARCH_STREAMS:
        lines.append(f"| `{query}` | {role} |")

    lines.extend(
        [
            "",
            "## New Candidates For Manual Review",
            "",
        ]
    )
    if new_candidates:
        lines.extend(markdown_table(new_candidates))
    else:
        lines.append("No new high-signal candidates were found in this run.")

    lines.extend(
        [
            "",
            "## Already Tracked Results",
            "",
        ]
    )
    lines.extend(markdown_table(tracked[:30]) if tracked else ["No already tracked entries appeared in this run."])

    lines.extend(
        [
            "",
            "## Low-Priority Or Likely Noise",
            "",
        ]
    )
    lines.extend(markdown_table(low_priority[:30]) if low_priority else ["No low-priority entries were retained in this run."])

    lines.extend(
        [
            "",
            "## Maintainer Next Step",
            "",
            "Open a repository-review issue for any candidate that looks promising, then apply `docs/repo-review-workflow.md` before promoting it to `README.md`.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    existing_links = read_existing_links()
    all_candidates: list[Candidate] = []
    for query, _role in SEARCH_STREAMS:
        all_candidates.extend(search_stream(query, args.per_page, existing_links))
        if args.sleep_seconds:
            time.sleep(args.sleep_seconds)
    candidates = dedupe(all_candidates)
    candidates.sort(
        key=lambda c: (
            c.tracked_status != "new to queue",
            {"candidate": 0, "review manually": 1, "already tracked": 2, "low priority": 3, "exclude": 4}.get(c.recommendation, 9),
            -c.stars,
            c.full_name.lower(),
        )
    )
    if args.limit:
        candidates = candidates[: args.limit]

    discovered_on = args.discovered_on or now_date()
    write_csv(candidates, args.output_csv)
    write_markdown(candidates, args.output_md, discovered_on)
    print(f"Wrote {len(candidates)} unique candidates to {args.output_md} and {args.output_csv}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-page", type=int, default=15, help="Results per GitHub search stream")
    parser.add_argument("--limit", type=int, default=0, help="Optional total output row limit")
    parser.add_argument("--sleep-seconds", type=float, default=0.2, help="Delay between search requests")
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--discovered-on", default="")
    args = parser.parse_args()
    try:
        run(args)
    except RuntimeError as exc:
        print(f"Discovery failed: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
