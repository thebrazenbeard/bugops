from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "reports" / "INCIDENT_REGISTRY_V1.json"

ID_RE = re.compile(r"BUG-\d{4}")
SEVERITY_RE = re.compile(r"SEV-[0-3]")
ISSUE_RE = re.compile(r"\*\*(?:GitHub issue|Issue):\*\*\s*#(\d+)", re.IGNORECASE)
PR_RE = re.compile(r"\*\*(?:Pull request|PR):\*\*\s*#(\d+)", re.IGNORECASE)
BRANCH_RE = re.compile(r"\*\*Incident branch:\*\*\s*`([^`]+)`", re.IGNORECASE)
STATUS_RE = re.compile(r"\*\*Status:\*\*\s*([A-Z_]+)", re.IGNORECASE)
SEV_LINE_RE = re.compile(r"\*\*Severity:\*\*\s*(SEV-[0-3])", re.IGNORECASE)

REQUIRED_TOPIC_GROUPS = (
    ("summary", ("incident summary", "short description")),
    ("intent", ("user intent",)),
    ("evidence", ("observed behavior", "evidence")),
    ("provenance", ("relevant provenance",)),
    ("failure chain", ("failure chain",)),
    ("root cause", ("root-cause analysis",)),
    ("impact", ("impact",)),
    ("corrective controls", ("corrective controls",)),
    ("regression", ("regression tests / acceptance criteria",)),
    ("effect boundary", ("effect boundary",)),
)


def _load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def _normalized_headings(text: str) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^#{2,4}\s+(.*)$", line.strip())
        if not match:
            continue
        heading = match.group(1).strip().lower()
        heading = re.sub(r"^\d+(?:\.\d+)*\.\s*", "", heading)
        headings.append(heading)
    return headings


def _topic_present(text: str, options: tuple[str, ...]) -> bool:
    headings = _normalized_headings(text)
    return any(
        any(option.lower() in heading for heading in headings)
        for option in options
    )


def validate_source() -> list[str]:
    errors: list[str] = []
    data = _load_registry()
    incidents = data.get("incidents", [])
    if not isinstance(incidents, list) or not incidents:
        return ["incident registry is empty or invalid"]

    ids: set[str] = set()
    issue_numbers: set[int] = set()
    pr_numbers: set[int] = set()
    registered_paths: set[str] = set()

    for item in incidents:
        incident_id = item.get("incident_id")
        path_value = item.get("report_path")
        if not isinstance(incident_id, str) or not ID_RE.fullmatch(incident_id):
            errors.append(f"invalid incident_id: {incident_id!r}")
            continue
        if incident_id in ids:
            errors.append(f"duplicate incident_id: {incident_id}")
        ids.add(incident_id)

        if not isinstance(path_value, str):
            errors.append(f"{incident_id}: report_path missing")
            continue
        registered_paths.add(path_value)
        report_path = ROOT / path_value
        if not report_path.is_file():
            errors.append(f"{incident_id}: missing report: {path_value}")
            continue

        text = report_path.read_text(encoding="utf-8")
        first_line = text.splitlines()[0] if text.splitlines() else ""
        if incident_id not in first_line:
            errors.append(f"{incident_id}: title does not contain incident ID")

        id_match = re.search(r"\*\*Incident ID:\*\*\s*(BUG-\d{4})", text)
        if not id_match or id_match.group(1) != incident_id:
            errors.append(f"{incident_id}: Incident ID metadata mismatch")

        status_match = STATUS_RE.search(text)
        expected_status = item.get("report_status")
        if not status_match:
            errors.append(f"{incident_id}: missing Status metadata")
        elif status_match.group(1).upper() != str(expected_status).upper():
            errors.append(
                f"{incident_id}: report status {status_match.group(1)} != registry {expected_status}"
            )

        sev_match = SEV_LINE_RE.search(text)
        if not sev_match or not SEVERITY_RE.fullmatch(sev_match.group(1).upper()):
            errors.append(f"{incident_id}: missing or invalid Severity metadata")

        issue_match = ISSUE_RE.search(text)
        issue_number = item.get("issue_number")
        if not isinstance(issue_number, int):
            errors.append(f"{incident_id}: registry issue_number missing")
        else:
            if issue_number in issue_numbers:
                errors.append(f"duplicate issue_number: {issue_number}")
            issue_numbers.add(issue_number)
            if not issue_match or int(issue_match.group(1)) != issue_number:
                errors.append(
                    f"{incident_id}: report issue reference does not match #{issue_number}"
                )

        pr_match = PR_RE.search(text)
        pr_number = item.get("pr_number")
        if not isinstance(pr_number, int):
            errors.append(f"{incident_id}: registry pr_number missing")
        else:
            if pr_number in pr_numbers:
                errors.append(f"duplicate pr_number: {pr_number}")
            pr_numbers.add(pr_number)
            if not pr_match or int(pr_match.group(1)) != pr_number:
                errors.append(
                    f"{incident_id}: report PR reference does not match #{pr_number}"
                )

        branch_match = BRANCH_RE.search(text)
        expected_branch = item.get("incident_branch")
        if not branch_match or branch_match.group(1) != expected_branch:
            errors.append(
                f"{incident_id}: incident branch does not match registry {expected_branch}"
            )

        for label, options in REQUIRED_TOPIC_GROUPS:
            if not _topic_present(text, options):
                errors.append(f"{incident_id}: missing required report topic: {label}")

    disk_reports = {
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in (ROOT / "reports").glob("BUG-*.md")
    }
    if disk_reports != registered_paths:
        missing_registry = sorted(disk_reports - registered_paths)
        missing_disk = sorted(registered_paths - disk_reports)
        if missing_registry:
            errors.append(f"unregistered reports: {missing_registry}")
        if missing_disk:
            errors.append(f"registry paths missing from disk: {missing_disk}")

    return errors


def _github_json(url: str, token: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "bugops-validator",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def validate_live() -> list[str]:
    errors: list[str] = []
    token = os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repository:
        return ["--live requires GITHUB_TOKEN and GITHUB_REPOSITORY"]

    data = _load_registry()
    base = f"https://api.github.com/repos/{repository}"
    for item in data.get("incidents", []):
        incident_id = item["incident_id"]
        issue_number = item["issue_number"]
        pr_number = item["pr_number"]

        try:
            issue = _github_json(f"{base}/issues/{issue_number}", token)
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            errors.append(f"{incident_id}: issue lookup failed: {exc}")
            continue

        expected_issue_state = item.get("expected_issue_state")
        if issue.get("state") != expected_issue_state:
            errors.append(
                f"{incident_id}: issue #{issue_number} state={issue.get('state')} "
                f"expected={expected_issue_state}"
            )

        try:
            pr = _github_json(f"{base}/pulls/{pr_number}", token)
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            errors.append(f"{incident_id}: PR lookup failed: {exc}")
            continue

        if item.get("expected_pr_merged") is True and not pr.get("merged_at"):
            errors.append(f"{incident_id}: PR #{pr_number} is not merged")
        if pr.get("head", {}).get("ref") != item.get("incident_branch"):
            errors.append(
                f"{incident_id}: PR #{pr_number} head={pr.get('head', {}).get('ref')} "
                f"expected={item.get('incident_branch')}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    errors = validate_source()
    if args.live:
        errors.extend(validate_live())

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    mode = "source + live GitHub" if args.live else "source"
    print(f"BugOps incident validation: PASS ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
