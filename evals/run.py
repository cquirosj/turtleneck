#!/usr/bin/env python3
"""Runner for the turtleneck evaluation suite."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import checks

EVALS = Path(__file__).resolve().parent
ROOT = EVALS.parent
RESULTS = EVALS / "results"
FIXTURES = EVALS / "fixtures"

DEFAULT_MODEL = "deepseek-v4.1-flash:cloud"
API_URL = "http://localhost:11434/api/chat"
HTTP_TIMEOUT = 300
BASELINE_SYSTEM = "You are a senior software architect. Answer the question."

JUDGE_CRITERIA = [
    "options_differ_in_kind",
    "tradeoff_stated_as_loss",
    "owner_questions_need_domain_knowledge",
    "no_invented_domain_facts",
]

JUDGE_SYSTEM = (
    "You are a strict evaluator of architecture decision records. "
    "Score each criterion from 0 to 5. Reply with a single JSON object and nothing else."
)

JUDGE_RUBRIC = """Score this architecture answer on four criteria, 0 to 5 each.

options_differ_in_kind: the options differ in kind, not in a parameter, and include a defer and a buy-or-reuse option.
tradeoff_stated_as_loss: the decision states the accepted trade-off as "we give up X to get Y", not benefits alone.
owner_questions_need_domain_knowledge: open questions genuinely need domain knowledge the answer could not have.
no_invented_domain_facts: no invented domain facts, quotes, statistics, or references presented as real.

Return strict JSON:
{"options_differ_in_kind": <0-5>, "tradeoff_stated_as_loss": <0-5>, "owner_questions_need_domain_knowledge": <0-5>, "no_invented_domain_facts": <0-5>, "notes": "<one sentence>"}
"""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_systems() -> dict[str, str]:
    base = "\n\n".join(
        [read_text(ROOT / "AGENTS.md"), read_text(ROOT / "skills/turtleneck/SKILL.md")]
        + [read_text(p) for p in sorted((ROOT / "skills/turtleneck/references").glob("*.md"))]
    )
    return {
        "baseline": BASELINE_SYSTEM,
        "skill": base,
        "skill+review": base + "\n\n" + read_text(ROOT / "skills/turtleneck-review/SKILL.md"),
        "skill+stress": base + "\n\n" + read_text(ROOT / "skills/turtleneck-stress/SKILL.md"),
    }


def system_key(case: checks.Case) -> str:
    if case.kind == "review":
        return "skill+review"
    if case.kind == "stress":
        return "skill+stress"
    return "skill"


def system_for(case: checks.Case, arm: str, systems: dict[str, str]) -> tuple[str, str]:
    if arm == "baseline":
        return systems["baseline"], "baseline"
    key = system_key(case)
    return systems[key], key


def call_model(model: str, system: str, user: str, timeout: int = HTTP_TIMEOUT) -> tuple[str, str | None, bool]:
    def attempt() -> tuple[str, str | None, bool]:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": 0},
        }
        request = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            return "", f"HTTPError: {exc}", 500 <= exc.code < 600
        except Exception as exc:
            return "", f"{type(exc).__name__}: {exc}", True
        try:
            parsed = json.loads(body)
            content = parsed["message"]["content"]
        except Exception as exc:
            return "", f"malformed model response: {type(exc).__name__}: {exc}", False
        if not isinstance(content, str):
            return "", "malformed model response: message.content is not a string", False
        return content, None, False

    content, error, retryable = attempt()
    if error and retryable:
        time.sleep(5)
        content, error, _ = attempt()
        return content, error, True
    return content, error, False


def coerce_score(value: object) -> int | None:
    try:
        number = int(float(value))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return max(0, min(5, number))


def parse_judge(text: str) -> dict:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    obj = None
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end > start:
        try:
            obj = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            obj = None
    if not isinstance(obj, dict):
        obj = None
    scores: dict = {}
    for key in JUDGE_CRITERIA:
        value = coerce_score(obj[key]) if obj and key in obj else None
        if value is None:
            match = re.search(rf'"?{key}"?\s*[:=]\s*"?(\d)', cleaned)
            if match:
                value = coerce_score(match.group(1))
        scores[key] = value
    if obj and "notes" in obj:
        scores["notes"] = str(obj["notes"])
    scores["parsed"] = obj is not None
    return scores


def build_judge_user(case: checks.Case, output: str) -> str:
    return (
        f"{JUDGE_RUBRIC}\n"
        f"--- QUESTION ---\n{case.prompt}\n"
        f"--- ANSWER ---\n{output}\n"
    )


def run_judge(model: str, case: checks.Case, output: str) -> dict:
    raw, error, retried = call_model(model, JUDGE_SYSTEM, build_judge_user(case, output))
    if error:
        result = {"error": error}
        if retried:
            result["retried"] = True
        return result
    scores = parse_judge(raw)
    scores["raw"] = raw
    if retried:
        scores["retried"] = True
    return scores


def base_entry(case: checks.Case, key: str) -> dict:
    return {
        "id": case.id,
        "case_id": case.id,
        "case_kind": case.kind,
        "level": case.level,
        "kind_label": case.kind + (f"/{case.level}" if case.level else ""),
        "system": key,
        "prompt": case.prompt,
        "output": "",
        "checks": [],
        "judge": None,
        "error": None,
        "retried": False,
        "skipped": False,
        "fixture": None,
    }


def dry_entries(case: checks.Case, key: str) -> list[dict]:
    entries = []
    for suffix in ("", ".fail"):
        path = FIXTURES / f"{case.id}{suffix}.md"
        if not path.exists():
            continue
        text = read_text(path)
        entry = base_entry(case, key)
        entry["id"] = f"{case.id}{suffix}"
        entry["output"] = text
        entry["fixture"] = str(path.relative_to(ROOT))
        entry["checks"] = [asdict(result) for result in checks.run_checks(case, text)]
        entries.append(entry)
    if not entries:
        entry = base_entry(case, key)
        entry["skipped"] = True
        entries.append(entry)
    return entries


def run_case(case: checks.Case, arm: str, systems: dict[str, str], args: argparse.Namespace) -> list[dict]:
    system, key = system_for(case, arm, systems)
    if args.dry_run:
        return dry_entries(case, key)
    output, error, retried = call_model(args.model, system, case.prompt)
    entry = base_entry(case, key)
    entry["output"] = output
    entry["retried"] = retried
    if error:
        entry["error"] = error
        entry["checks"] = [asdict(checks.CheckResult("model_error", False, error))]
        return [entry]
    entry["checks"] = [asdict(result) for result in checks.run_checks(case, output)]
    if args.judge:
        if case.kind in ("decide", "decided"):
            entry["judge"] = run_judge(args.model, case, output)
        else:
            entry["judge"] = {"skipped": "rubric applies to decision records only"}
    return [entry]


def run_arm(arm: str, cases: list[checks.Case], systems: dict[str, str], args: argparse.Namespace) -> list[dict]:
    if not cases:
        return []
    entries: list[dict] = []
    if args.concurrency <= 1 or args.dry_run:
        for case in cases:
            entries.extend(run_case(case, arm, systems, args))
        return entries
    results: dict[int, list[dict]] = {}
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = {
            executor.submit(run_case, case, arm, systems, args): index
            for index, case in enumerate(cases)
        }
        for future in as_completed(futures):
            results[futures[future]] = future.result()
    for index in range(len(cases)):
        entries.extend(results[index])
    return entries


def counts(entries: list[dict]) -> tuple[int, int]:
    passed = sum(1 for entry in entries for check in entry["checks"] if check["passed"])
    total = sum(len(entry["checks"]) for entry in entries)
    return passed, total


def render_table(entries: list[dict]) -> str:
    lines = ["| case | kind | checks | failed |", "|---|---|---|---|"]
    for entry in entries:
        if entry["skipped"]:
            lines.append(f"| {entry['id']} | {entry['kind_label']} | skipped | |")
            continue
        passed = sum(1 for check in entry["checks"] if check["passed"])
        total = len(entry["checks"])
        failed = ", ".join(check["name"] for check in entry["checks"] if not check["passed"])
        lines.append(f"| {entry['id']} | {entry['kind_label']} | {passed}/{total} | {failed} |")
    return "\n".join(lines)


def aggregate_by_case(entries: list[dict]) -> dict[str, tuple[int, int]]:
    aggregate: dict[str, tuple[int, int]] = {}
    for entry in entries:
        if entry["skipped"]:
            continue
        passed, total = aggregate.get(entry["case_id"], (0, 0))
        aggregate[entry["case_id"]] = (
            passed + sum(1 for check in entry["checks"] if check["passed"]),
            total + len(entry["checks"]),
        )
    return aggregate


def render_delta(skill_entries: list[dict], baseline_entries: list[dict]) -> str:
    skill = aggregate_by_case(skill_entries)
    baseline = aggregate_by_case(baseline_entries)
    lines = ["| case | skill | baseline | delta (passed) |", "|---|---|---|---|"]
    for case_id in skill:
        if case_id not in baseline:
            continue
        skill_passed, skill_total = skill[case_id]
        base_passed, base_total = baseline[case_id]
        lines.append(
            f"| {case_id} | {skill_passed}/{skill_total} | {base_passed}/{base_total} | {skill_passed - base_passed:+d} |"
        )
    return "\n".join(lines)


def pass_rate(entries: list[dict]) -> tuple[int, int, float]:
    passed, total = counts(entries)
    rate = (100.0 * passed / total) if total else 0.0
    return passed, total, rate


def write_results(arm: str, entries: list[dict], systems: dict[str, str], args: argparse.Namespace, timestamp: str) -> Path:
    RESULTS.mkdir(parents=True, exist_ok=True)
    used = sorted({entry["system"] for entry in entries})
    payload = {
        "arm": arm,
        "model": args.model,
        "timestamp": timestamp,
        "dry_run": args.dry_run,
        "judge": args.judge and not args.dry_run,
        "system_prompts": {key: systems[key] for key in used},
        "cases": entries,
    }
    stem = Path(args.cases).stem
    prefix = "" if stem == "cases" else f"{stem}-"
    path = RESULTS / f"{timestamp}-{prefix}{arm}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the turtleneck evaluation suite.")
    parser.add_argument("--arm", choices=["skill", "baseline", "both"], required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--only", default=None, help="single case id, or a comma-separated list")
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--judge", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cases", default=str(EVALS / "cases.json"), help="case file; results are prefixed with its stem when it is not cases.json")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    all_cases = checks.load_cases(Path(args.cases))
    cases = all_cases
    if args.only:
        wanted = {item.strip() for item in args.only.split(",") if item.strip()}
        cases = [case for case in all_cases if case.id in wanted]
        if not cases:
            print(f"no case matched --only {args.only!r}", file=sys.stderr)
            return 2
    if args.concurrency < 1:
        print("--concurrency must be at least 1", file=sys.stderr)
        return 2
    if args.dry_run and args.judge:
        print("note: --judge is ignored with --dry-run (no model calls)", file=sys.stderr)

    systems = build_systems()
    arms = ["skill", "baseline"] if args.arm == "both" else [args.arm]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    results_by_arm: dict[str, list[dict]] = {}
    for arm in arms:
        entries = run_arm(arm, cases, systems, args)
        results_by_arm[arm] = entries
        if args.dry_run:
            print(f"# arm: {arm} | model: {args.model} | dry-run: True")
        else:
            path = write_results(arm, entries, systems, args, timestamp)
            print(f"# arm: {arm} | model: {args.model} | dry-run: False | results: {path}")
        print(render_table(entries))
        passed, total, rate = pass_rate(entries)
        print(f"\narm pass rate: {passed}/{total} checks ({rate:.1f}%)\n")

    if args.arm == "both":
        print("# delta, skill vs baseline")
        print(render_delta(results_by_arm["skill"], results_by_arm["baseline"]))
        print()
        for arm in ("skill", "baseline"):
            passed, total, rate = pass_rate(results_by_arm[arm])
            print(f"{arm} aggregate pass rate: {passed}/{total} checks ({rate:.1f}%)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
