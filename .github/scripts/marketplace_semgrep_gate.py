"""Fail CI on the Semgrep findings that would block a Frappe Marketplace release.

Reads, on stdin, the JSON report of `semgrep scan` run with frappe/marketplace's
validation/semgrep-rules and applies the marketplace's own blocking rule: a
finding blocks when its rule sets `is_blocking: true` or its severity maps to
Critical or Major. Others are reported as warnings and never fail the job.
"""

import json
import sys

# frappe/marketplace validation/utils/report.py
SEVERITY_LABELS = {
	"CRITICAL": "Critical",
	"ERROR": "Critical",
	"HIGH": "Major",
	"WARNING": "Minor",
	"MEDIUM": "Minor",
	"LOW": "Info",
	"INFO": "Info",
}
BLOCKING = {"Critical", "Major"}


def main() -> int:
	report = json.load(sys.stdin)

	blocking = 0
	for finding in report.get("results", []):
		extra = finding.get("extra", {})
		label = SEVERITY_LABELS.get(str(extra.get("severity", "INFO")).upper(), "Info")
		is_blocking = extra.get("metadata", {}).get("is_blocking") is True or label in BLOCKING
		blocking += is_blocking
		rule = finding.get("check_id", "").rsplit(".", 1)[-1]
		message = " ".join(extra.get("message", "").split())
		level = "error" if is_blocking else "warning"
		print(
			f"::{level} file={finding.get('path')},line={finding.get('start', {}).get('line')}"
			f",title=Marketplace {label}: {rule}::{message}"
		)

	errors = report.get("errors", [])
	for error in errors:
		print(f"::error title=Semgrep error::{' '.join(str(error.get('message', error)).split())}")

	total = len(report.get("results", []))
	print(f"{total} marketplace finding(s), {blocking} blocking, {len(errors)} Semgrep error(s).")
	return 1 if blocking or errors else 0


if __name__ == "__main__":
	sys.exit(main())
