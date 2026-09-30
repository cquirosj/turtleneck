"""Deterministic checks for the turtleneck evaluation suite."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Case:
    id: str
    kind: str
    prompt: str
    level: str | None = None
    expected_tags: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class CheckResult:
    name: str
    passed: bool
    reason: str


def load_cases(path: str | Path) -> list[Case]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    items = raw["cases"] if isinstance(raw, dict) else raw
    cases = []
    for item in items:
        cases.append(
            Case(
                id=item["id"],
                kind=item["kind"],
                prompt=item["prompt"],
                level=item.get("level"),
                expected_tags=list(item.get("expected_tags", [])),
                notes=item.get("notes", ""),
            )
        )
    return cases


def nonempty_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]


def _ok(name: str) -> CheckResult:
    return CheckResult(name, True, "ok")


def _verdict(name: str, condition: bool, reason: str) -> CheckResult:
    return _ok(name) if condition else CheckResult(name, False, reason)


def _heading_re(phrase: str) -> re.Pattern[str]:
    return re.compile(r"^#{2,6}[ \t]*" + re.escape(phrase) + r"\b", re.I | re.M)


def has_heading(text: str, phrase: str) -> bool:
    return bool(_heading_re(phrase).search(text))


def section_body(text: str, phrase: str) -> str:
    match = _heading_re(phrase).search(text)
    if not match:
        return ""
    rest = text[match.end():]
    nxt = re.search(r"^#{1,6}[ \t]", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


REQUIRED_HEADINGS = [
    ("heading_two_floors", "Two floors"),
    ("heading_options", "Options"),
    ("heading_stressors", "Stressors"),
    ("heading_price", "Price"),
    ("heading_cross_examination", "Cross-examination"),
    ("heading_decision", "Decision"),
    ("heading_flips_if", "Flips if"),
    ("heading_owner_decisions", "Owner decisions"),
]

OPTION_RE = re.compile(r"^\s*(?:[-*][ \t]+)?(?:\*\*)?([A-Z])[.)](?:\*\*)?[ \t]+\S")


def option_lines(text: str) -> list[str]:
    body = section_body(text, "Options")
    return [line for line in body.splitlines() if OPTION_RE.match(line)]


def _is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\|[\s\-:|]+\|", line))


def table_rows(body: str) -> list[str]:
    lines = body.splitlines()
    sep_index = next(
        (index for index, line in enumerate(lines) if _is_separator(line.strip())),
        None,
    )
    if sep_index is None:
        return []
    rows = []
    for line in lines[sep_index + 1:]:
        stripped = line.strip()
        if stripped.startswith("|") and not _is_separator(stripped):
            rows.append(stripped)
        else:
            break
    return rows


def stressor_rows(text: str) -> list[str]:
    return table_rows(section_body(text, "Stressors"))


def owner_decision_questions(text: str) -> list[str]:
    body = section_body(text, "Owner decisions")
    return [line.strip() for line in body.splitlines() if line.strip().endswith("?")]


def _decide_headings(text: str) -> list[CheckResult]:
    results = []
    for name, phrase in REQUIRED_HEADINGS:
        if has_heading(text, phrase):
            results.append(_ok(name))
        else:
            results.append(CheckResult(name, False, f'missing heading "{phrase}"'))
    return results


def _decide_options(text: str) -> list[CheckResult]:
    options = option_lines(text)
    results = [
        _verdict("option_count", len(options) >= 3, f"{len(options)} option lines, need at least 3"),
        _verdict(
            "option_defers",
            any("defer" in option.lower() for option in options),
            "no option mentions defer",
        ),
        _verdict(
            "option_buys_or_reuses",
            any(re.search(r"\b(buy|reuse)\b", option, re.I) for option in options),
            "no option mentions buy or reuse",
        ),
    ]
    return results


def _decide_stressors(text: str, min_rows: int, max_rows: int | None) -> list[CheckResult]:
    rows = stressor_rows(text)
    if max_rows is None:
        count_reason = f"{len(rows)} stressor rows, need at least {min_rows}"
        count_ok = len(rows) >= min_rows
    else:
        count_reason = f"{len(rows)} stressor rows, need {min_rows} to {max_rows}"
        count_ok = min_rows <= len(rows) <= max_rows
    absurd = [row for row in rows if "absurd" in row.lower()]
    return [
        _verdict("stressor_row_count", count_ok, count_reason),
        _verdict("absurd_stressor_count", len(absurd) >= 2, f"{len(absurd)} rows contain absurd, need at least 2"),
    ]


BULLET_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+\S")


def _flips_if_bullet(text: str) -> CheckResult:
    body = section_body(text, "Flips if")
    has_bullet = any(BULLET_RE.match(line) for line in body.splitlines())
    return _verdict("flips_if_bullet", has_bullet, 'no bullet line in "Flips if"')


def _decide_tail(text: str) -> list[CheckResult]:
    decision = section_body(text, "Decision")
    lower = text.lower()
    return [
        _verdict("give_up_in_decision", "give up" in decision.lower(), '"give up" not in the Decision section'),
        _verdict("elevator_pass", "elevator pass" in lower, '"Elevator pass" not found'),
        _verdict("residuality_pass", "residuality pass" in lower, '"Residuality pass" not found'),
        _verdict("owner_stressors_present", "owner stressors" in lower, '"Owner stressors" not found'),
        _verdict(
            "owner_decision_question",
            bool(owner_decision_questions(text)),
            "Owner decisions section has no line ending in ?",
        ),
        _flips_if_bullet(text),
    ]


def decide_full_checks(case: Case, text: str) -> list[CheckResult]:
    results = _decide_headings(text)
    results += _decide_options(text)
    results += _decide_stressors(text, 8, 12)
    results += _decide_tail(text)
    return results


def decide_deep_checks(case: Case, text: str) -> list[CheckResult]:
    results = _decide_headings(text)
    results += _decide_options(text)
    results += _decide_stressors(text, 20, None)
    results += _decide_tail(text)
    lower = text.lower()
    results.append(_verdict("incidence_word", "incidence" in lower, '"incidence" not found'))
    results.append(_verdict("contagion_word", "contagion" in lower, '"contagion" not found'))
    return results


def decide_napkin_checks(case: Case, text: str) -> list[CheckResult]:
    lines = nonempty_lines(text)
    return [
        _verdict("napkin_line_limit", len(lines) <= 12, f"{len(lines)} non-empty lines, max 12"),
        _verdict("give_up_present", "give up" in text.lower(), '"give up" not found'),
        _verdict("has_question", "?" in text, "no ? found"),
        _verdict(
            "no_table_rows",
            not any(line.strip().startswith("|") for line in text.splitlines()),
            "a line starts with |",
        ),
    ]


def gate_checks(case: Case, text: str) -> list[CheckResult]:
    lines = nonempty_lines(text)
    phrases = ["cheap to undo", "not architecture", "move on", "ponytail"]
    found = [phrase for phrase in phrases if phrase in text.lower()]
    return [
        _verdict("gate_line_limit", len(lines) <= 8, f"{len(lines)} non-empty lines, max 8"),
        _verdict("gate_no_stressors_heading", "## Stressors" not in text, "contains ## Stressors"),
        _verdict(
            "gate_no_table_rows",
            not any(line.strip().startswith("|") for line in text.splitlines()),
            "a line starts with |",
        ),
        _verdict(
            "gate_phrase",
            bool(found),
            "none of: " + ", ".join(phrases),
        ),
    ]


def decided_checks(case: Case, text: str) -> list[CheckResult]:
    lower = text.lower()
    banned = [
        phrase
        for phrase in [
            "i recommend",
            "instead, consider",
            "you should reconsider",
            "reconsider the decision",
            "reopen the decision",
        ]
        if phrase in lower
    ]
    near_options = bool(re.search(r"options?[^\n]{0,40}\bone\b", text, re.I))
    options = option_lines(text)
    if near_options:
        option_reason = '"one" appears near "options"'
    elif len(options) == 1:
        option_reason = "Options section has exactly one option line"
    else:
        option_reason = f'"one" not near "options" and Options has {len(options)} option lines'
    return [
        CheckResult("decided_one_option", near_options or len(options) == 1, option_reason),
        _verdict("give_up_present", "give up" in lower, '"give up" not found'),
        _verdict("no_relitigation", not banned, "contains " + ", ".join(banned)),
    ]


REVIEW_TAGS = [
    "one-floor",
    "unexplored",
    "unpriced",
    "unstressed",
    "justified-after",
    "no-flip",
    "unowned",
    "invented",
    "cliché",
    "reinvented",
]
GAP_RE = re.compile(
    r"^(?:§|L)\S.*?:\s*(" + "|".join(re.escape(tag) for tag in REVIEW_TAGS) + r"):",
    re.M,
)
VERDICT_RE = re.compile(r"^\d+ gaps\. (?:decision|description|deck)\.?\s*$")


def review_checks(case: Case, text: str) -> list[CheckResult]:
    found = GAP_RE.findall(text)
    missing = [tag for tag in case.expected_tags if tag not in found]
    lines = nonempty_lines(text)
    verdict = lines[-1] if lines else ""
    return [
        _verdict("review_gap_lines", bool(found), "no gap lines matched the review format"),
        _verdict(
            "review_expected_tags",
            not missing,
            "missing tags: " + ", ".join(missing) if missing else "",
        ),
        _verdict(
            "review_verdict_line",
            bool(VERDICT_RE.match(verdict.strip())),
            f"last non-empty line is not a verdict: {verdict[:60]!r}",
        ),
    ]


def stress_checks(case: Case, text: str) -> list[CheckResult]:
    lower = text.lower()
    rows = [line for line in text.splitlines() if line.strip().startswith("|")]
    has_separator = any(_is_separator(line.strip()) for line in rows)
    no_decision = "## Decision" not in text and "i recommend" not in lower
    return [
        _verdict("stress_components", "Components:" in text, '"Components:" not found'),
        _verdict("stress_table", bool(rows) and has_separator, "no markdown table with a separator row"),
        _verdict("stress_attractors", "attractors" in lower, '"Attractors" not found'),
        _verdict("stress_owner_stressors", "owner stressors" in lower, '"Owner stressors" not found'),
        _verdict("stress_no_decision", no_decision, 'contains "## Decision" or "I recommend"'),
    ]


BANNED_PATTERNS = [
    ("banned_best_practice", re.compile(r"best practice", re.I), '"best practice"'),
    ("banned_industry_standard", re.compile(r"industry standard", re.I), '"industry standard"'),
    ("banned_future_proof", re.compile(r"future[- ]proof", re.I), '"future-proof"'),
    ("banned_it_depends", re.compile(r"\bit depends\b(?! on)", re.I), '"it depends" without "on"'),
    ("banned_architect_quote", re.compile(r"(Hohpe|O'Reilly|Fowler|Uncle Bob) (says|said|argues|wrote)", re.I), "named architect quote"),
    ("banned_microservices_monolith", re.compile(r"microservices vs\.? monolith", re.I), '"microservices vs monolith"'),
]

QUALITY_RE = re.compile(r"scalab|maintainab|performan|reliab", re.I)
RATING_EXACT_RE = re.compile(r"^(high|medium|low)$", re.I)

REVIEW_EXEMPT_BANNED = {
    "banned_best_practice",
    "banned_industry_standard",
    "banned_future_proof",
    "banned_it_depends",
    "banned_microservices_monolith",
}


def _rating_row_offender(line: str) -> str | None:
    stripped = line.strip()
    if not stripped.startswith("|") or _is_separator(stripped):
        return None
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    nonempty = [cell for cell in cells if cell]
    if not nonempty or not QUALITY_RE.search(nonempty[0]):
        return None
    if any(RATING_EXACT_RE.match(cell) for cell in nonempty[1:]):
        return stripped
    return None


def banned_checks(case: Case, text: str) -> list[CheckResult]:
    results = []
    for name, pattern, label in BANNED_PATTERNS:
        if case.kind == "review" and name in REVIEW_EXEMPT_BANNED:
            continue
        match = pattern.search(text)
        results.append(
            _verdict(name, match is None, f"contains {label}")
        )
    offender = next(
        (row for line in text.splitlines() if (row := _rating_row_offender(line))),
        None,
    )
    results.append(
        _verdict(
            "banned_quality_ratings",
            offender is None,
            f"table row rates a quality word: {offender[:60]}" if offender else "",
        )
    )
    return results


def run_checks(case: Case, output_text: str) -> list[CheckResult]:
    text = output_text or ""
    if case.kind == "decide":
        level = case.level or "full"
        if level == "napkin":
            results = decide_napkin_checks(case, text)
        elif level == "deep":
            results = decide_deep_checks(case, text)
        else:
            results = decide_full_checks(case, text)
    elif case.kind == "gate":
        results = gate_checks(case, text)
    elif case.kind == "decided":
        results = decided_checks(case, text)
    elif case.kind == "review":
        results = review_checks(case, text)
    elif case.kind == "stress":
        results = stress_checks(case, text)
    else:
        results = [CheckResult("unknown_kind", False, f"unknown case kind {case.kind!r}")]
    return results + banned_checks(case, text)
