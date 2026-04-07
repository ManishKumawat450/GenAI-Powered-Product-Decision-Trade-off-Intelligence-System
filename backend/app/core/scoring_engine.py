"""
Deterministic, rule-based scoring engine for product decision trade-offs.
All scores are reproducible and grounded in stored option/constraint text.
"""
from __future__ import annotations
import re
from typing import Any

DEFAULT_CRITERIA = [
    {"name": "User Value", "description": "Direct value delivered to end users"},
    {"name": "Engineering Effort", "description": "Development complexity and team capacity (lower effort = higher score)"},
    {"name": "Time-to-Market", "description": "Speed of delivery relative to business window"},
    {"name": "Risk", "description": "Technical, market, or execution risk (lower risk = higher score)"},
    {"name": "Cost", "description": "Financial investment required (lower cost = higher score)"},
    {"name": "Maintainability", "description": "Long-term maintenance burden (lower burden = higher score)"},
    {"name": "Strategic Alignment", "description": "Alignment with company strategy and long-term vision"},
    {"name": "Compliance/Privacy", "description": "Regulatory and privacy requirements adherence"},
]

# Keyword signals: (patterns, score_adjustment)
_SIGNALS: dict[str, dict[str, list[tuple[list[str], int]]]] = {
    "User Value": {
        "positive": [
            (["user.facing", "ux", "user experience", "customer.centric", "customer value", "end.user",
              "usability", "delight", "satisfaction", "onboarding"], 3),
            (["user", "customer", "experience", "value"], 1),
        ],
        "negative": [
            (["internal only", "backend only", "no user", "invisible to user"], -3),
            (["technical only", "infrastructure only"], -2),
        ],
    },
    "Engineering Effort": {
        # HIGH score = LOW effort (good)
        "positive": [
            (["off.the.shelf", "existing library", "reuse", "plug.in", "out.of.the.box",
              "no additional dev", "minimal dev"], 3),
            (["simple", "straightforward", "existing", "standard library", "proven approach"], 2),
            (["small", "quick", "lightweight"], 1),
        ],
        "negative": [
            (["custom build", "rebuild from scratch", "new infrastructure", "complex architecture",
              "significant engineering", "months of work", "requires research"], -3),
            (["custom", "complex", "heavy", "large team", "specialized"], -2),
            (["new", "experimental", "prototype"], -1),
        ],
    },
    "Time-to-Market": {
        "positive": [
            (["fast", "quick", "days", "week", "rapid", "immediate", "instant",
              "already exists", "pre.built", "out.of.the.box"], 3),
            (["existing", "proven", "familiar", "straightforward"], 2),
            (["moderate", "reasonable timeline"], 1),
        ],
        "negative": [
            (["months", "long timeline", "slow", "requires research", "requires new hire",
              "requires training", "year"], -3),
            (["several", "extended", "lengthy", "complex setup"], -2),
        ],
    },
    "Risk": {
        # HIGH score = LOW risk (good)
        "positive": [
            (["proven", "stable", "battle.tested", "well.tested", "low risk", "minimal risk",
              "reliable", "mature", "established", "widely used"], 3),
            (["existing", "standard", "familiar", "documented"], 2),
            (["manageable", "mitigated", "acceptable"], 1),
        ],
        "negative": [
            (["experimental", "unproven", "high risk", "bleeding edge", "untested",
              "unknown", "uncertain", "volatile"], -3),
            (["new technology", "new approach", "prototype", "research"], -2),
            (["risk", "concern", "challenge"], -1),
        ],
    },
    "Cost": {
        # HIGH score = LOW cost (good)
        "positive": [
            (["free", "open source", "no additional cost", "existing budget", "included",
              "already licensed", "no license fee"], 3),
            (["low cost", "affordable", "cost.effective", "minimal cost"], 2),
            (["within budget", "reasonable cost"], 1),
        ],
        "negative": [
            (["expensive", "significant investment", "new license", "requires new hire",
              "high cost", "costly", "major investment"], -3),
            (["cost", "license fee", "subscription", "paid"], -1),
        ],
    },
    "Maintainability": {
        "positive": [
            (["modular", "clean architecture", "well.documented", "standard patterns",
              "easy to maintain", "maintainable", "testable"], 3),
            (["standard", "documented", "simple codebase", "readable"], 2),
            (["organized", "structured"], 1),
        ],
        "negative": [
            (["technical debt", "workaround", "hack", "fragile", "brittle",
              "hard to maintain", "spaghetti", "monolithic"], -3),
            (["complex", "tightly coupled", "hard to test"], -2),
            (["manual", "custom"], -1),
        ],
    },
    "Strategic Alignment": {
        "positive": [
            (["strategic", "long.term", "platform", "scalable", "vision", "roadmap",
              "future.proof", "company strategy", "aligns with"], 3),
            (["growth", "competitive advantage", "differentiator"], 2),
            (["planned", "approved", "fits"], 1),
        ],
        "negative": [
            (["tactical", "short.term fix", "workaround", "one.off", "temporary",
              "stops scaling", "not scalable"], -3),
            (["limited", "narrow", "niche"], -1),
        ],
    },
    "Compliance/Privacy": {
        "positive": [
            (["gdpr", "compliant", "privacy.by.design", "secure", "audit trail",
              "data protection", "regulation", "certified", "iso", "soc2"], 3),
            (["privacy", "security", "encrypted", "access control"], 2),
            (["documented", "reviewed"], 1),
        ],
        "negative": [
            (["non.compliant", "data exposure", "privacy risk", "security risk",
              "unaudited", "pii risk"], -3),
            (["unclear compliance", "unknown data handling"], -1),
        ],
    },
}


def _contains_any(text: str, patterns: list[str]) -> bool:
    """Check if text contains any of the regex patterns (word boundaries)."""
    text_lower = text.lower()
    for pat in patterns:
        if re.search(r"\b" + pat.replace(".", r"[\s\-_]?") + r"\b", text_lower):
            return True
    return False


def _score_criterion(criterion_name: str, text: str) -> tuple[float, str]:
    """
    Return (raw_score 1-10, explanation).
    Base score is 5 (neutral). Signals move it up/down capped to [1,10].
    """
    signals = _SIGNALS.get(criterion_name, {})
    score = 5.0
    reasons: list[str] = []

    for patterns, adjustment in signals.get("positive", []):
        if _contains_any(text, patterns):
            score += adjustment
            matched = next((p for p in patterns if _contains_any(text, [p])), patterns[0])
            reasons.append(f"positive signal '{matched.replace('.', ' ')}' (+{adjustment})")

    for patterns, adjustment in signals.get("negative", []):
        if _contains_any(text, patterns):
            score += adjustment
            matched = next((p for p in patterns if _contains_any(text, [p])), patterns[0])
            reasons.append(f"negative signal '{matched.replace('.', ' ')}' ({adjustment})")

    score = max(1.0, min(10.0, score))
    if reasons:
        explanation = f"Score {score:.1f}/10 for {criterion_name}: " + "; ".join(reasons) + "."
    else:
        explanation = f"Score {score:.1f}/10 for {criterion_name}: No strong signals found; default score applied."
    return score, explanation


def _build_constraint_text(constraints: list[dict]) -> str:
    """Build a single string from all constraints for signal detection."""
    parts = []
    for c in constraints:
        parts.append(f"{c.get('type', '')} {c.get('description', '')} {c.get('value', '') or ''}")
    return " ".join(parts)


def _apply_constraint_penalties(
    criterion_name: str,
    raw_score: float,
    constraint_text: str,
) -> tuple[float, str]:
    """Apply score adjustments based on decision-level constraints."""
    adjustment = 0.0
    note = ""
    if criterion_name == "Time-to-Market" and _contains_any(constraint_text, ["tight", "urgent", "asap", "critical"]):
        if raw_score < 5:
            adjustment = -1.0
            note = " [penalised -1 due to tight time constraint]"
    if criterion_name == "Cost" and _contains_any(constraint_text, ["limited budget", "no budget", "budget constraint", "budget limited"]):
        if raw_score < 5:
            adjustment = -1.0
            note = " [penalised -1 due to limited budget constraint]"
    return max(1.0, raw_score + adjustment), note


class ScoringEngine:
    """
    Deterministic scoring engine. Works with plain dicts so it is fully unit-testable
    without any database connection.
    """

    def compute_scores(
        self,
        decision: dict,
        options: list[dict],
        criteria_weights: list[dict],
        criteria: list[dict],
    ) -> dict[str, Any]:
        """
        Parameters
        ----------
        decision : dict with keys title, problem_statement, success_metrics
        options  : list of dicts with keys id, label, name, description
        criteria_weights : list of dicts with keys criterion_id, weight
        criteria : list of dicts with keys id, name, description

        Returns
        -------
        dict with keys: rankings, trade_off_matrix, narrative
        """
        # Index criteria and weights
        crit_by_id = {c["id"]: c for c in criteria}
        weight_by_cid = {w["criterion_id"]: w["weight"] for w in criteria_weights}

        # Normalise weights so they sum to 1
        total_w = sum(weight_by_cid.values()) or 1.0
        norm_weights = {cid: w / total_w for cid, w in weight_by_cid.items()}

        constraint_text = _build_constraint_text(decision.get("constraints", []))
        decision_text_prefix = (
            f"{decision.get('problem_statement', '')} "
            f"{decision.get('success_metrics', '')} "
        )

        option_results = []
        for opt in options:
            full_text = f"{decision_text_prefix} {opt.get('name', '')} {opt.get('description', '')}"
            per_criterion: list[dict] = []
            total_weighted = 0.0

            for cid, c in crit_by_id.items():
                raw, explanation = _score_criterion(c["name"], full_text)
                raw, note = _apply_constraint_penalties(c["name"], raw, constraint_text)
                if note:
                    explanation += note
                w = norm_weights.get(cid, 0.0)
                weighted = raw * w
                total_weighted += weighted
                per_criterion.append({
                    "criterion_id": cid,
                    "criterion_name": c["name"],
                    "raw_score": round(raw, 2),
                    "weighted_score": round(weighted, 4),
                    "explanation": explanation,
                })

            # Normalise total to 0-100
            total_score = round(total_weighted * 10, 2)
            risks = self._derive_risks(per_criterion)
            recommendations = self._derive_recommendations(opt, per_criterion, total_score)

            option_results.append({
                "option_id": opt["id"],
                "option_label": opt.get("label", ""),
                "option_name": opt.get("name", ""),
                "total_score": total_score,
                "scores": per_criterion,
                "risks": risks,
                "recommendations": recommendations,
            })

        # Sort by total score descending
        option_results.sort(key=lambda x: x["total_score"], reverse=True)
        for i, r in enumerate(option_results):
            r["rank"] = i + 1

        trade_off_matrix = self._build_matrix(option_results, crit_by_id)
        narrative = self._build_narrative(decision, option_results)

        return {
            "rankings": option_results,
            "trade_off_matrix": trade_off_matrix,
            "narrative": narrative,
        }

    @staticmethod
    def _derive_risks(per_criterion: list[dict]) -> list[str]:
        risks: list[str] = []
        for s in per_criterion:
            if s["raw_score"] <= 3:
                name = s["criterion_name"]
                if name == "Risk":
                    risks.append("High execution/technical risk may jeopardise delivery.")
                elif name == "Engineering Effort":
                    risks.append("High engineering effort could delay the timeline.")
                elif name == "Cost":
                    risks.append("Significant cost investment required; budget approval needed.")
                elif name == "Time-to-Market":
                    risks.append("Slow time-to-market may miss the competitive window.")
                elif name == "Maintainability":
                    risks.append("Low maintainability may increase long-term tech debt.")
                elif name == "Compliance/Privacy":
                    risks.append("Potential compliance or privacy gaps need legal review.")
        return risks or ["No significant risks identified at current scoring level."]

    @staticmethod
    def _derive_recommendations(opt: dict, scores: list[dict], total: float) -> list[str]:
        recs: list[str] = []
        if total >= 70:
            recs.append(f"Option '{opt.get('name')}' is a strong candidate; prioritise for MVP.")
        elif total >= 50:
            recs.append(f"Option '{opt.get('name')}' is viable; review trade-offs before committing.")
        else:
            recs.append(f"Option '{opt.get('name')}' scores low overall; consider as a fallback only.")

        low_criteria = [s["criterion_name"] for s in scores if s["raw_score"] <= 4]
        if low_criteria:
            recs.append(f"Key improvement areas: {', '.join(low_criteria)}.")
        return recs

    @staticmethod
    def _build_matrix(option_results: list[dict], crit_by_id: dict) -> list[dict]:
        criteria_names = [c["name"] for c in crit_by_id.values()]
        matrix = []
        for r in option_results:
            row: dict = {"option": r["option_name"], "label": r["option_label"], "total": r["total_score"]}
            score_map = {s["criterion_name"]: s["raw_score"] for s in r["scores"]}
            for cname in criteria_names:
                row[cname] = score_map.get(cname, 5.0)
            matrix.append(row)
        return matrix

    @staticmethod
    def _build_narrative(decision: dict, ranked: list[dict]) -> str:
        top = ranked[0]
        lines = [
            f"Decision: {decision.get('title', 'Untitled')}",
            "",
            "Weighted Scoring Analysis Results:",
            "",
        ]
        for r in ranked:
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(r["rank"], f"#{r['rank']}")
            top_criteria = sorted(r["scores"], key=lambda x: x["raw_score"], reverse=True)[:3]
            top_names = ", ".join(s["criterion_name"] for s in top_criteria)
            lines.append(
                f"{medal} Rank {r['rank']}: {r['option_name']} (Score: {r['total_score']}/100)"
            )
            lines.append(f"   Strengths: {top_names}")
            if r["risks"] and r["risks"][0] != "No significant risks identified at current scoring level.":
                lines.append(f"   Risks: {r['risks'][0]}")
            lines.append("")

        lines += [
            "Recommendation:",
            f"Based on the weighted scoring model, '{top['option_name']}' is the top-ranked option "
            f"with a score of {top['total_score']}/100. "
        ]
        if len(ranked) > 1:
            runner = ranked[1]
            diff = round(top["total_score"] - runner["total_score"], 1)
            lines.append(
                f"It outperforms '{runner['option_name']}' by {diff} points. "
            )
        lines += [
            "",
            "Key Trade-offs:",
        ]
        for r in ranked:
            low = [s["criterion_name"] for s in r["scores"] if s["raw_score"] <= 4]
            high = [s["criterion_name"] for s in r["scores"] if s["raw_score"] >= 7]
            line = f"  • {r['option_name']}:"
            if high:
                line += f" strong in {', '.join(high[:2])}"
            if low:
                line += f"; weak in {', '.join(low[:2])}"
            lines.append(line)

        lines += [
            "",
            "Note: All scores are deterministic and based on keyword analysis of option descriptions.",
            "Adjust option descriptions and criteria weights to refine results.",
        ]
        return "\n".join(lines)


scoring_engine = ScoringEngine()
