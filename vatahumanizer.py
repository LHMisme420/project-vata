#!/usr/bin/env python3
"""
vatahumanizer.py

Human-facing utilities + soul-scoring engine for VATA.

Requirements:
- Safe to import from any module (no side effects at import time)
- Provides VataHumanizer class for human-readable summaries
- Provides a CLI that:
    python vatahumanizer.py <file> [--level ...] [--target ...]
  and prints a line:
    SOUL SCORE: <number>
- Never crashes on bad input; always returns a nonzero score.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Union
import sys
import re
import tokenize
from pathlib import Path

ScoreType = Union[int, float]


# ============================================================
# Humanizer config and class (for imports / other modules)
# ============================================================

@dataclass
class HumanizerConfig:
    """Configuration for how we present scores and labels."""
    low_threshold: ScoreType = 0.25
    medium_threshold: ScoreType = 0.6
    high_threshold: ScoreType = 0.85

    low_label: str = "Low"
    medium_label: str = "Medium"
    high_label: str = "High"

    clamp_scores: bool = True
    include_numeric: bool = True


@dataclass
class VataHumanizer:
    """
    Core humanizer used across the project.

    - No heavy imports
    - No side effects at import time
    - Safe to use from CLI, tests, and web app
    """
    config: HumanizerConfig = field(default_factory=HumanizerConfig)

    def _clamp(self, score: ScoreType) -> ScoreType:
        if not self.config.clamp_scores:
            return score
        if score < 0:
            return 0.0
        if score > 1:
            return 1.0
        return float(score)

    def _bucket_label(self, score: ScoreType) -> str:
        s = self._clamp(score)
        if s < self.config.low_threshold:
            return self.config.low_label
        if s < self.config.medium_threshold:
            return self.config.medium_label
        if s < self.config.high_threshold:
            return self.config.high_label
        return self.config.high_label

    def humanize_score(self, score: ScoreType, label: Optional[str] = None) -> str:
        s = self._clamp(score)
        bucket = label or self._bucket_label(s)
        if self.config.include_numeric:
            return f"{bucket} confidence ({s:.2f})"
        return f"{bucket} confidence"

    def humanize_authorship(self, ai_score: ScoreType, human_score: ScoreType) -> str:
        ai_s = self._clamp(ai_score)
        human_s = self._clamp(human_score)

        if ai_s > human_s:
            dominant = "AI-generated"
        elif human_s > ai_s:
            dominant = "Human-authored"
        else:
            dominant = "Indeterminate"

        return (
            f"Authorship assessment: {dominant}. "
            f"AI likelihood: {ai_s:.2f}, Human likelihood: {human_s:.2f}."
        )

    def humanize_file_result(
        self,
        path: str,
        scores: Dict[str, ScoreType],
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        extra = extra or {}
        ai = scores.get("ai_likelihood")
        human = scores.get("human_likelihood")
        soul = scores.get("soul_score")

        parts: List[str] = [f"File: {path}"]

        if soul is not None:
            parts.append(f"Soul score: {self.humanize_score(soul)}")

        if ai is not None and human is not None:
            parts.append(self.humanize_authorship(ai, human))

        flags = extra.get("flags") or []
        notes = extra.get("notes") or []

        if flags:
            parts.append("Flags: " + ", ".join(str(f) for f in flags))
        if notes:
            parts.append("Notes: " + " | ".join(str(n) for n in notes))

        return "  ".join(parts)

    def humanize_batch(
        self,
        results: List[Dict[str, Any]],
        path_key: str = "path",
        scores_key: str = "scores",
        extra_key: str = "extra",
    ) -> List[str]:
        humanized: List[str] = []
        for item in results:
            path = item.get(path_key, "<unknown>")
            scores = item.get(scores_key, {}) or {}
            extra = item.get(extra_key, {}) or {}
            humanized.append(self.humanize_file_result(path, scores, extra))
        return humanized

    @classmethod
    def from_dict(cls, cfg: Optional[Dict[str, Any]] = None) -> "VataHumanizer":
        cfg = cfg or {}
        hc = HumanizerConfig(
            low_threshold=cfg.get("low_threshold", 0.25),
            medium_threshold=cfg.get("medium_threshold", 0.6),
            high_threshold=cfg.get("high_threshold", 0.85),
            low_label=cfg.get("low_label", "Low"),
            medium_label=cfg.get("medium_label", "Medium"),
            high_label=cfg.get("high_label", "High"),
            clamp_scores=cfg.get("clamp_scores", True),
            include_numeric=cfg.get("include_numeric", True),
        )
        return cls(config=hc)


default_humanizer = VataHumanizer()


def humanize_score(score: ScoreType) -> str:
    return default_humanizer.humanize_score(score)


def humanize_file_result(
    path: str,
    scores: Dict[str, ScoreType],
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    return default_humanizer.humanize_file_result(path, scores, extra or {})


# ============================================================
# Soul scoring engine (used by CI CLI)
# ============================================================

def safe_read(path: str) -> str:
    try:
        return Path(path).read_text(errors="ignore")
    except Exception:
        return ""


def score_comment_density(text: str) -> float:
    lines = text.splitlines()
    if not lines:
        return 0.0
    comment_lines = sum(1 for l in lines if l.strip().startswith("#"))
    return comment_lines / len(lines)


def score_identifier_style(text: str) -> float:
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text)
    if not tokens:
        return 0.0

    good = 0
    total = 0

    for t in tokens:
        total += 1
        if "_" in t and len(t) > 3:
            good += 1
        elif len(t) > 6:
            good += 1

    return good / total if total else 0.0


def score_complexity(text: str) -> float:
    hits = len(re.findall(r"\b(def|class|if|for|while|try|except|with)\b", text))
    if hits == 0:
        return 0.0
    return min(1.0, hits / 40)


def score_docstrings(text: str) -> float:
    triple = re.findall(r'"""(.*?)"""', text, flags=re.DOTALL)
    if not triple:
        return 0.0
    return min(1.0, len(triple) / 5)


def score_token_balance(path: str) -> float:
    try:
        with open(path, "rb") as f:
            list(tokenize.tokenize(f.readline))
        return 1.0
    except Exception:
        return 0.2


def compute_soul_score(path: str) -> int:
    text = safe_read(path)

    if not text.strip():
        return 5  # minimal but nonzero

    c1 = score_comment_density(text)
    c2 = score_identifier_style(text)
    c3 = score_complexity(text)
    c4 = score_docstrings(text)
    c5 = score_token_balance(path)

    score = (
        0.25 * c1 +
        0.25 * c2 +
        0.20 * c3 +
        0.15 * c4 +
        0.15 * c5
    )

    final = int(score * 100)
    return max(final, 5)


# ============================================================
# CLI entrypoint (used by GitHub Actions)
# ============================================================

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: vatahumanizer.py <file> [--level ...] [--target ...]")
        sys.exit(0)

    path = sys.argv[1]

    # Ignore extra flags like --level, --target; CI only cares about SOUL SCORE
    score = compute_soul_score(path)

    print(f"FILE: {path}")
    print(f"SOUL SCORE: {score}")


if __name__ == "__main__":
    main()
