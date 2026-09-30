#!/usr/bin/env python3
"""LLM judge for the architecture quality of turtleneck kata records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

EVALS = Path(__file__).resolve().parent
ROOT = EVALS.parent
RESULTS = EVALS / "results"

API_URL = "http://localhost:11434/api/chat"
HTTP_TIMEOUT = 300
PI_TIMEOUT = 600
OLLAMA_PREFIX = "ollama/"

# (key, scorecard abbreviation, rubric text)
CRITERIA: list[tuple[str, str, str]] = [
    (
        "load_bearing",
        "lb",
        "did it pick the decision(s) hardest to undo for THIS brief, rather than a generic component list?",
    ),
    (
        "uses_brief",
        "brief",
        "does the record use the brief's specific users, scale, and requirements rather than generic statements?",
    ),
    (
        "options_differ_in_kind",
        "opts",
        "options differ in kind, including a real defer and a real buy/reuse option that fit this domain.",
    ),
    (
        "stressors_specific",
        "stress",
        "stressors come from THIS domain and business (regulator, customer type, seasonality, device, geography), not a generic list.",
    ),
    (
        "coupling_found",
        "coupl",
        "names at least one non-obvious coupling revealed by stressors, and derives a boundary from it.",
    ),
    (
        "price_realistic",
        "price",
        "build/run/undo prices are plausible for the stated team and scale and name who pays.",
    ),
    (
        "flips_observable",
        "flips",
        "flip conditions are facts someone could observe, not vibes.",
    ),
    (
        "owner_questions_real",
        "owner",
        "owner questions need domain knowledge the model could not have, and a real client would recognize them as the right questions.",
    ),
    (
        "no_invented_facts",
        "facts",
        "5 means nothing asserted beyond the brief; deduct for invented regulations, numbers, vendors stated as facts.",
    ),
    (
        "cliche_free",
        "cliche",
        '5 means no pattern-by-name without stressor, no -ility ratings, no "best practice"/"industry standard", no appeals to named architects.',
    ),
]

CRITERION_KEYS = [key for key, _, _ in CRITERIA]

JUDGE_SYSTEM = (
    "You are a senior software architect reviewing a junior's decision record for a client brief. "
    "Score strictly. 5 is what you would sign. 3 is competent but generic. 0 is missing or wrong. "
    "Reply with one JSON object only."
)


def build_rubric() -> str:
    lines = ["Score this architecture decision record on ten criteria, 0 to 5 each."]
    lines.extend(f"{key}: {text}" for key, _, text in CRITERIA)
    lines.append("")
    lines.append(
        "Return strict JSON with one object per criterion, a score and a one-line why, "
        "plus the two free-text fields: " + _rubric_example()
    )
    return "\n".join(lines)


def _rubric_example() -> str:
    body = ", ".join(f'"{key}": {{"score": 0, "why": "..."}}' for key in CRITERION_KEYS)
    return "{" + body + ', "strongest_line": "...", "weakest_move": "..."}'


RUBRIC = build_rubric()


def _strip_fences(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def coerce_score(value: object) -> int | None:
    try:
        number = int(float(value))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return max(0, min(5, number))


def _fallback_score(cleaned: str, key: str) -> int | None:
    match = re.search(rf'"?{re.escape(key)}"?\s*[:=]', cleaned)
    if not match:
        return None
    tail = cleaned[match.end(): match.end() + 100]
    digit = re.search(r"(?<![\d.])([0-5])(?![\d.])", tail)
    return int(digit.group(1)) if digit else None


def _fallback_string(cleaned: str, key: str) -> str:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*"((?:[^"\\]|\\.)*)"', cleaned)
    if not match:
        return ""
    try:
        return json.loads(f'"{match.group(1)}"')
    except json.JSONDecodeError:
        return match.group(1)


def parse_judge(text: str) -> dict:
    cleaned = _strip_fences(text)
    obj = None
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end > start:
        try:
            loaded = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            loaded = None
        if isinstance(loaded, dict):
            obj = loaded
    scores: dict[str, int | None] = {}
    whys: dict[str, str] = {}
    for key in CRITERION_KEYS:
        value = obj.get(key) if obj else None
        if isinstance(value, dict):
            score = coerce_score(value.get("score"))
            why = str(value.get("why", ""))
        else:
            score = coerce_score(value)
            why = ""
        if score is None:
            score = _fallback_score(cleaned, key)
        if not why:
            why = ""
        scores[key] = score
        whys[key] = why
    strongest = obj.get("strongest_line") if obj and isinstance(obj.get("strongest_line"), str) else ""
    weakest = obj.get("weakest_move") if obj and isinstance(obj.get("weakest_move"), str) else ""
    return {
        "scores": scores,
        "whys": whys,
        "strongest_line": strongest or _fallback_string(cleaned, "strongest_line"),
        "weakest_move": weakest or _fallback_string(cleaned, "weakest_move"),
        "parsed": obj is not None,
    }


def build_judge_user(prompt: str, output: str) -> str:
    return f"{RUBRIC}\n--- BRIEF ---\n{prompt}\n--- RECORD ---\n{output}\n"


def call_ollama(model: str, system: str, user: str, timeout: int = HTTP_TIMEOUT) -> tuple[str, str | None]:
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
        return "", f"HTTPError: {exc}"
    except Exception as exc:
        return "", f"{type(exc).__name__}: {exc}"
    try:
        content = json.loads(body)["message"]["content"]
    except Exception as exc:
        return "", f"malformed model response: {type(exc).__name__}: {exc}"
    if not isinstance(content, str):
        return "", "malformed model response: message.content is not a string"
    return content, None


def call_pi(model: str, system: str, user: str, timeout: int = PI_TIMEOUT) -> tuple[str, str | None]:
    command = ["pi", "-p", "--model", model, "--system-prompt", system, user]
    try:
        process = subprocess.run(
            command,
            cwd="/tmp",
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception as exc:
        return "", f"{type(exc).__name__}: {exc}"
    if process.returncode != 0:
        detail = (process.stderr or "").strip().splitlines()
        tail = detail[-1] if detail else "no stderr"
        return process.stdout or "", f"pi exited {process.returncode}: {tail}"
    if not process.stdout.strip():
        return "", "pi returned empty stdout"
    return process.stdout, None


def route_model(
    model: str,
    system: str,
    user: str,
    *,
    ollama: object = None,
    pi: object = None,
) -> tuple[str, str | None]:
    if model.startswith(OLLAMA_PREFIX):
        call = ollama or call_ollama
        return call(model[len(OLLAMA_PREFIX):], system, user)  # type: ignore[operator]
    call = pi or call_pi
    return call(model, system, user)  # type: ignore[operator]


def judge_case(case: dict, model: str, *, ollama: object = None, pi: object = None) -> dict:
    case_id = case.get("id") or case.get("case_id") or "?"
    blank = {
        "id": case_id,
        "scores": {key: None for key in CRITERION_KEYS},
        "whys": {key: "" for key in CRITERION_KEYS},
        "strongest_line": "",
        "weakest_move": "",
        "raw": "",
        "error": None,
    }
    if case.get("error"):
        blank["error"] = f"case error: {case['error']}"
        return blank
    if case.get("skipped"):
        blank["error"] = "skipped case"
        return blank
    output = case.get("output") or ""
    if not output.strip():
        blank["error"] = "no output to judge"
        return blank
    raw, error = route_model(
        model,
        JUDGE_SYSTEM,
        build_judge_user(case.get("prompt") or "", output),
        ollama=ollama,
        pi=pi,
    )
    if error:
        blank["raw"] = raw or ""
        blank["error"] = error
        return blank
    parsed = parse_judge(raw)
    return {
        "id": case_id,
        "scores": parsed["scores"],
        "whys": parsed["whys"],
        "strongest_line": parsed["strongest_line"],
        "weakest_move": parsed["weakest_move"],
        "raw": raw,
        "error": None,
        "parsed": parsed["parsed"],
    }


def judge_all(
    cases: list[dict],
    model: str,
    concurrency: int,
    *,
    ollama: object = None,
    pi: object = None,
) -> list[dict]:
    if concurrency <= 1 or len(cases) <= 1:
        return [judge_case(case, model, ollama=ollama, pi=pi) for case in cases]
    ordered: dict[int, dict] = {}
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {
            executor.submit(judge_case, case, model, ollama=ollama, pi=pi): index
            for index, case in enumerate(cases)
        }
        for future in as_completed(futures):
            ordered[futures[future]] = future.result()
    return [ordered[index] for index in range(len(cases))]


def _numbers(values: list[object]) -> list[int]:
    return [value for value in values if isinstance(value, int)]


def render_scorecard(judgements: list[dict], model: str = "", results_path: str = "") -> str:
    headers = [abbrev for _, abbrev, _ in CRITERIA]
    lines = [f"# Kata quality judge | model: {model}", ""]
    if results_path:
        lines.append(f"results: {results_path}")
        lines.append("")
    lines.append("| case | " + " | ".join(headers) + " | total/50 |")
    lines.append("|" + "---|" * (len(headers) + 2))
    for judgement in judgements:
        scores = judgement.get("scores") or {}
        cells = []
        total = 0
        for key in CRITERION_KEYS:
            value = scores.get(key)
            if isinstance(value, int):
                cells.append(str(value))
                total += value
            else:
                cells.append("-")
        lines.append(f"| {judgement.get('id', '?')} | " + " | ".join(cells) + f" | {total} |")
    means: list[float | None] = []
    for key in CRITERION_KEYS:
        values = _numbers([(judgement.get("scores") or {}).get(key) for judgement in judgements])
        means.append(sum(values) / len(values) if values else None)
    totals = [
        sum(v for v in (judgement.get("scores") or {}).values() if isinstance(v, int))
        for judgement in judgements
        if any(isinstance(v, int) for v in (judgement.get("scores") or {}).values())
    ]
    total_mean = sum(totals) / len(totals) if totals else 0.0
    mean_cells = [f"{mean:.1f}" if mean is not None else "-" for mean in means]
    lines.append("| mean | " + " | ".join(mean_cells) + f" | {total_mean:.1f} |")
    lines.append("")
    for judgement in judgements:
        move = judgement.get("weakest_move") or judgement.get("error") or "-"
        lines.append(f"- {judgement.get('id', '?')}: {move}")
    ranked = sorted(
        ((mean, key, abbrev) for mean, (key, abbrev, _) in zip(means, CRITERIA) if mean is not None),
        key=lambda item: item[0],
    )
    lowest = ", ".join(f"{key} ({mean:.1f})" for mean, key, _ in ranked[:3])
    lines.append("")
    lines.append(f"Lowest mean criteria: {lowest or '-'}")
    return "\n".join(lines)


def system_prompt_hash(payload: dict) -> str | None:
    prompts = payload.get("system_prompts")
    if not isinstance(prompts, dict) or not prompts:
        return None
    first = next(iter(prompts.values()), None)
    if not isinstance(first, str):
        return None
    return hashlib.sha256(first.encode("utf-8")).hexdigest()


def git_commit() -> str | None:
    try:
        process = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return None
    if process.returncode != 0:
        return None
    return process.stdout.strip() or None


def select_cases(cases: list[dict], only: str | None) -> list[dict]:
    if not only:
        return cases
    wanted = {item.strip() for item in only.split(",") if item.strip()}
    return [case for case in cases if (case.get("id") or case.get("case_id")) in wanted]


def write_outputs(
    results_path: str,
    model: str,
    judgements: list[dict],
    payload: dict,
    timestamp: str,
) -> tuple[Path, Path]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    record = {
        "results": results_path,
        "judge_model": model,
        "timestamp": timestamp,
        "git_commit": git_commit(),
        "system_prompt_sha256": system_prompt_hash(payload),
        "cases": judgements,
    }
    json_path = RESULTS / f"{timestamp}-kata-judge.json"
    json_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    scorecard = render_scorecard(judgements, model=model, results_path=results_path)
    md_path = RESULTS / f"{timestamp}-kata-scorecard.md"
    md_path.write_text(scorecard + "\n", encoding="utf-8")
    return json_path, md_path


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Judge the architecture quality of turtleneck kata records.")
    parser.add_argument("--results", required=True, help="path to a results file written by run.py")
    parser.add_argument("--judge-model", required=True, help="ollama/<name> for Ollama, anything else for the pi CLI")
    parser.add_argument("--only", default=None, help="single case id, or a comma-separated list")
    parser.add_argument("--concurrency", type=int, default=2)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.concurrency < 1:
        print("--concurrency must be at least 1", file=sys.stderr)
        return 2
    path = Path(args.results)
    if not path.exists():
        print(f"results file not found: {path}", file=sys.stderr)
        return 2
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"could not read results file: {exc}", file=sys.stderr)
        return 2
    cases = payload.get("cases") or []
    selected = select_cases(cases, args.only)
    if not selected:
        print("no case matched the results file", file=sys.stderr)
        return 2

    judgements = judge_all(selected, args.judge_model, args.concurrency)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path, md_path = write_outputs(args.results, args.judge_model, judgements, payload, timestamp)
    print(render_scorecard(judgements, model=args.judge_model, results_path=args.results))
    print(f"\nwrote {json_path}\nwrote {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
