"""Unit tests for the deterministic scoring engine."""
import pytest
from app.core.scoring_engine import ScoringEngine, scoring_engine


def make_decision(title="Test Decision", problem="Problem", constraints=None):
    return {
        "id": 1, "title": title, "problem_statement": problem,
        "success_metrics": "Fast and good", "constraints": constraints or []
    }


def make_criteria():
    return [
        {"id": 1, "name": "User Value", "description": "User value"},
        {"id": 2, "name": "Engineering Effort", "description": "Effort"},
        {"id": 3, "name": "Time-to-Market", "description": "Speed"},
        {"id": 4, "name": "Risk", "description": "Risk level"},
        {"id": 5, "name": "Cost", "description": "Cost"},
        {"id": 6, "name": "Maintainability", "description": "Maintenance"},
        {"id": 7, "name": "Strategic Alignment", "description": "Strategy"},
        {"id": 8, "name": "Compliance/Privacy", "description": "Compliance"},
    ]


def make_weights(equal=True):
    if equal:
        return [{"criterion_id": i, "weight": 0.125} for i in range(1, 9)]
    return [
        {"criterion_id": 1, "weight": 0.30},
        {"criterion_id": 2, "weight": 0.20},
        {"criterion_id": 3, "weight": 0.20},
        {"criterion_id": 4, "weight": 0.15},
        {"criterion_id": 5, "weight": 0.10},
        {"criterion_id": 6, "weight": 0.05},
        {"criterion_id": 7, "weight": 0.00},
        {"criterion_id": 8, "weight": 0.00},
    ]


class TestScoringEngine:
    def setup_method(self):
        self.engine = ScoringEngine()

    def test_returns_expected_keys(self):
        options = [{"id": 1, "label": "A", "name": "Opt A", "description": "simple existing"}]
        result = self.engine.compute_scores(make_decision(), options, make_weights(), make_criteria())
        assert "rankings" in result
        assert "trade_off_matrix" in result
        assert "narrative" in result

    def test_all_scores_within_range(self):
        options = [
            {"id": 1, "label": "A", "name": "Alpha", "description": "user experience simple existing free open source proven maintainable"},
            {"id": 2, "label": "B", "name": "Beta", "description": "custom build experimental expensive complex unproven"},
        ]
        result = self.engine.compute_scores(make_decision(), options, make_weights(), make_criteria())
        for ranking in result["rankings"]:
            for s in ranking["scores"]:
                assert 1.0 <= s["raw_score"] <= 10.0, f"Score out of range: {s}"

    def test_total_score_range(self):
        options = [
            {"id": 1, "label": "A", "name": "Alpha", "description": "simple existing proven low risk free open source"},
        ]
        result = self.engine.compute_scores(make_decision(), options, make_weights(), make_criteria())
        assert 0 <= result["rankings"][0]["total_score"] <= 100

    def test_better_option_ranked_first(self):
        """Option with strong positive keywords should outrank option with negative keywords."""
        options = [
            {
                "id": 1, "label": "A", "name": "Bad Option",
                "description": "custom build experimental unproven expensive rebuild from scratch complex new infrastructure high risk"
            },
            {
                "id": 2, "label": "B", "name": "Good Option",
                "description": "proven stable existing library simple quick free open source low risk modular maintainable user experience"
            },
        ]
        result = self.engine.compute_scores(make_decision(), options, make_weights(), make_criteria())
        ranked = result["rankings"]
        assert ranked[0]["option_name"] == "Good Option", (
            f"Expected Good Option first, got {ranked[0]['option_name']} ({ranked[0]['total_score']}) "
            f"vs {ranked[1]['option_name']} ({ranked[1]['total_score']})"
        )

    def test_rank_assigned_correctly(self):
        options = [
            {"id": 1, "label": "A", "name": "A", "description": "experimental complex expensive unproven"},
            {"id": 2, "label": "B", "name": "B", "description": "simple existing proven free modular"},
            {"id": 3, "label": "C", "name": "C", "description": "standard documented reliable low cost"},
        ]
        result = self.engine.compute_scores(make_decision(), options, make_weights(), make_criteria())
        ranks = [r["rank"] for r in result["rankings"]]
        assert sorted(ranks) == [1, 2, 3]

    def test_narrative_mentions_top_option(self):
        options = [
            {"id": 1, "label": "A", "name": "FeatureFlags",
             "description": "proven stable existing free open source simple modular user value"},
        ]
        result = self.engine.compute_scores(make_decision(), options, make_weights(), make_criteria())
        assert "FeatureFlags" in result["narrative"]

    def test_trade_off_matrix_structure(self):
        options = [
            {"id": 1, "label": "A", "name": "Option1", "description": "simple existing"},
            {"id": 2, "label": "B", "name": "Option2", "description": "complex custom"},
        ]
        result = self.engine.compute_scores(make_decision(), options, make_weights(), make_criteria())
        matrix = result["trade_off_matrix"]
        assert len(matrix) == 2
        assert "option" in matrix[0]
        assert "total" in matrix[0]

    def test_risks_generated(self):
        options = [
            {"id": 1, "label": "A", "name": "Risky",
             "description": "experimental unproven high risk new technology significant investment complex"},
        ]
        result = self.engine.compute_scores(make_decision(), options, make_weights(), make_criteria())
        assert len(result["rankings"][0]["risks"]) > 0

    def test_recommendations_generated(self):
        options = [
            {"id": 1, "label": "A", "name": "Safe",
             "description": "proven stable simple existing free modular user experience"},
        ]
        result = self.engine.compute_scores(make_decision(), options, make_weights(), make_criteria())
        assert len(result["rankings"][0]["recommendations"]) > 0

    def test_weighted_sum_correct(self):
        """Verify weighted_score = raw_score * normalised_weight for each criterion."""
        options = [{"id": 1, "label": "A", "name": "TestOpt", "description": "simple existing proven"}]
        weights = [{"criterion_id": i, "weight": 0.125} for i in range(1, 9)]
        criteria = make_criteria()
        result = self.engine.compute_scores(make_decision(), options, weights, criteria)
        ranking = result["rankings"][0]
        expected_total = sum(s["weighted_score"] for s in ranking["scores"]) * 10
        assert abs(ranking["total_score"] - expected_total) < 0.01

    # ── Seed scenario tests ────────────────────────────────────────────────────
    def test_pricing_experiment_feature_flags_ranks_first(self):
        """Feature Flags should rank #1 for the pricing experiment scenario."""
        options = [
            {
                "id": 1, "label": "A", "name": "A/B Testing Framework",
                "description": (
                    "Build a custom A/B testing framework. New infrastructure required. "
                    "Complex architecture with custom build. High engineering effort. "
                    "Several months of work. Significant investment in new team capacity."
                ),
            },
            {
                "id": 2, "label": "B", "name": "Feature Flags",
                "description": (
                    "Use an existing feature flag approach with proven, stable patterns. "
                    "Reuse existing infrastructure. Simple, straightforward implementation. "
                    "Quick rollout, within existing budget, no additional cost. "
                    "Low risk, battle-tested technique. Modular, well-documented, maintainable."
                ),
            },
            {
                "id": 3, "label": "C", "name": "Manual Rollout",
                "description": (
                    "Manual process, no additional dev required. Free, no additional cost. "
                    "Fragile workaround, technical debt. Hard to maintain. Short-term fix only."
                ),
            },
        ]
        weights = [
            {"criterion_id": 1, "weight": 0.20}, {"criterion_id": 2, "weight": 0.15},
            {"criterion_id": 3, "weight": 0.20}, {"criterion_id": 4, "weight": 0.15},
            {"criterion_id": 5, "weight": 0.10}, {"criterion_id": 6, "weight": 0.10},
            {"criterion_id": 7, "weight": 0.05}, {"criterion_id": 8, "weight": 0.05},
        ]
        constraints = [
            {"type": "time", "description": "Must be live within 6 weeks", "value": "tight"},
            {"type": "budget", "description": "Limited budget", "value": "limited budget"},
        ]
        result = self.engine.compute_scores(
            make_decision(constraints=constraints), options, weights, make_criteria()
        )
        top = result["rankings"][0]
        assert top["option_name"] == "Feature Flags", (
            f"Expected Feature Flags #1 but got {top['option_name']} ({top['total_score']})"
        )

    def test_mobile_mvp_full_parity_ranks_last(self):
        """Full Feature Parity should rank last for the mobile MVP scenario."""
        options = [
            {
                "id": 1, "label": "A", "name": "Core Flows Only",
                "description": (
                    "Authentication, dashboard, and core user journey only. "
                    "Simple, straightforward, existing patterns. Quick to deliver. "
                    "Within existing budget. Low risk, proven approach. Maintainable clean architecture."
                ),
            },
            {
                "id": 2, "label": "B", "name": "Core Plus Onboarding",
                "description": (
                    "Core flows plus onboarding for new users. User-facing experience, customer-centric. "
                    "Manageable scope, within budget. Proven patterns, low risk. Well-documented, maintainable."
                ),
            },
            {
                "id": 3, "label": "C", "name": "Full Feature Parity",
                "description": (
                    "Complete feature parity with the web app. Rebuild from scratch, complex architecture. "
                    "High engineering effort. Several months, significant investment, expensive. "
                    "High risk, experimental mobile patterns. Hard to maintain."
                ),
            },
        ]
        weights = [
            {"criterion_id": 1, "weight": 0.20}, {"criterion_id": 2, "weight": 0.20},
            {"criterion_id": 3, "weight": 0.20}, {"criterion_id": 4, "weight": 0.15},
            {"criterion_id": 5, "weight": 0.10}, {"criterion_id": 6, "weight": 0.10},
            {"criterion_id": 7, "weight": 0.05}, {"criterion_id": 8, "weight": 0.00},
        ]
        result = self.engine.compute_scores(
            make_decision(), options, weights, make_criteria()
        )
        last = result["rankings"][-1]
        assert last["option_name"] == "Full Feature Parity", (
            f"Expected Full Feature Parity last but got {last['option_name']} ({last['total_score']})"
        )
