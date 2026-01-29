"""
vatahumanizer.py

Utility to turn raw VATA scores / metadata into
human-readable summaries for CLI, logs, and UI.
This version is intentionally dependency-light and
safe to import from any context (CI, tests, app).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Union


ScoreType = Union[int, float]


@dataclass
class HumanizerConfig:
    """Configuration for how we present scores and labels."""
    low_threshold: ScoreType = 0.25
    medium_threshold: ScoreType = 0.6
    high_threshold: ScoreType = 0.85

    # Optional labels that can be overridden by callers
    low_label: str = "Low"
    medium_label: str = "Medium"
    high_label: str = "High"

    # When True, we clamp scores into [0, 1]
    clamp_scores: bool = True

    # Optional: include raw numeric score in human text
    include_numeric: bool = True


@dataclass
class VataHumanizer:
    """
    Core humanizer used across the project.

    This class is intentionally minimal and robust:
    - No heavy imports
    - No side effects at import time
    - Safe to use from CLI, tests, and web app
    """
    config: HumanizerConfig = field(default_factory=HumanizerConfig)

    # ---- Core helpers -----------------------------------------------------

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

    # ---- Public API -------------------------------------------------------

    def humanize_score(self, score: ScoreType, label: Optional[str] = None) -> str:
        """
        Turn a numeric score into a short human-readable phrase.

        Example:
            0.12 -> "Low confidence (0.12)"
        """
        s = self._clamp(score)
        bucket = label or self._bucket_label(s)

        if self.config.include_numeric:
            return f"{bucket} confidence ({s:.2f})"
        return f"{bucket} confidence"

    def humanize_authorship(self, ai_score: ScoreType, human_score: ScoreType) -> str:
        """
        Human-readable summary for AI vs human authorship likelihood.
        Assumes scores are in [0, 1] or will be clamped there.
        """
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
        """
        Humanize a per-file result object.

        Expected `scores` keys (flexible, but common):
            - 'ai_likelihood'
            - 'human_likelihood'
            - 'soul_score' (or similar)
        """
        extra = extra or {}
        ai = scores.get("ai_likelihood")
        human = scores.get("human_likelihood")
        soul = scores.get("soul_score")

        parts: List[str] = [f"File: {path}"]

        if soul is not None:
            parts.append(f"Soul score: {self.humanize_score(soul)}")

        if ai is not None and human is not None:
            parts.append(self.humanize_authorship(ai, human))

        # Attach any extra flags / notes
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
        """
        Humanize a batch of results.

        Each result is expected to be a dict like:
            {
                "path": "some/file.py",
                "scores": {"ai_likelihood": 0.8, "human_likelihood": 0.2, "soul_score": 0.1},
                "extra": {"flags": [...], "notes": [...]}
            }
        """
        humanized: List[str] = []
        for item in results:
            path = item.get(path_key, "<unknown>")
            scores = item.get(scores_key, {}) or {}
            extra = item.get(extra_key, {}) or {}
            humanized.append(self.humanize_file_result(path, scores, extra))
        return humanized

    # ---- Factory helpers --------------------------------------------------

    @classmethod
    def from_dict(cls, cfg: Optional[Dict[str, Any]] = None) -> "VataHumanizer":
        """
        Convenience constructor from a plain dict, e.g. loaded from YAML/JSON.
        Unknown keys are ignored.
        """
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


# Optional: a module-level default instance for quick use
default_humanizer = VataHumanizer()


def humanize_score(score: ScoreType) -> str:
    """
    Convenience function so existing code can call:

        from vatahumanizer import humanize_score

    without needing to instantiate the class explicitly.
    """
    return default_humanizer.humanize_score(score)


def humanize_file_result(
    path: str,
    scores: Dict[str, ScoreType],
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    return default_humanizer.humanize_file_result(path, scores, extra or {})
if __name__ == "__main__":
    import sys
    import random

    # Accept a filename but ignore it for now
    path = sys.argv[1] if len(sys.argv) > 1 else "<unknown>"

    # Temporary deterministic placeholder score
    # Replace with real scoring later
    soul_score = 80

    print(f"FILE: {path}")
    print(f"SOUL SCORE: {soul_score}")
