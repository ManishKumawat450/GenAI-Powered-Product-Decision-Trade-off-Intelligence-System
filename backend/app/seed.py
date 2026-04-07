"""
Seed script: creates roles, users, workspace, and 3 decision scenarios with evaluations.
Run: python -m app.seed
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal, engine
from app.models import *  # noqa: F401, F403 – registers all models
from app.database import Base
from app.core.security import hash_password
from app.core.scoring_engine import scoring_engine, DEFAULT_CRITERIA
from app.models.user import User, Role
from app.models.workspace import Workspace
from app.models.decision import Decision, Constraint, Option, ReasoningOutput
from app.models.criteria import Criterion, DecisionCriterionWeight, OptionScore
from app.models.collaboration import AuditLog
from datetime import datetime


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # ── Roles ─────────────────────────────────────────────────────────────
        roles = {}
        for name in ("admin", "pm", "viewer"):
            r = db.query(Role).filter(Role.name == name).first()
            if not r:
                r = Role(name=name)
                db.add(r)
                db.flush()
            roles[name] = r

        # ── Users ─────────────────────────────────────────────────────────────
        users_data = [
            ("admin@example.com", "admin", "Admin123!", "admin"),
            ("pm@example.com", "pm_user", "PM123!", "pm"),
            ("viewer@example.com", "viewer_user", "Viewer123!", "viewer"),
        ]
        users = {}
        for email, username, pwd, role_name in users_data:
            u = db.query(User).filter(User.email == email).first()
            if not u:
                u = User(email=email, username=username, hashed_password=hash_password(pwd))
                u.roles.append(roles[role_name])
                db.add(u)
                db.flush()
            users[role_name] = u

        db.commit()

        # ── Criteria ──────────────────────────────────────────────────────────
        criteria_objs = {}
        for c in DEFAULT_CRITERIA:
            cr = db.query(Criterion).filter(Criterion.name == c["name"]).first()
            if not cr:
                cr = Criterion(name=c["name"], description=c["description"], is_global=True)
                db.add(cr)
                db.flush()
            criteria_objs[c["name"]] = cr
        db.commit()

        # ── Workspace ─────────────────────────────────────────────────────────
        ws = db.query(Workspace).filter(Workspace.name == "Product Innovation Hub").first()
        if not ws:
            ws = Workspace(
                name="Product Innovation Hub",
                description="Central workspace for product strategy decisions",
                goals="Accelerate product decisions with data-driven trade-off analysis",
                context="B2B SaaS company, 50-person engineering team, Series B stage",
                owner_id=users["admin"].id,
            )
            db.add(ws)
            db.commit()
            db.refresh(ws)

        # ── Decision Scenarios ────────────────────────────────────────────────
        scenarios = [
            {
                "title": "Pricing Experiment Rollout",
                "problem_statement": (
                    "How should we roll out pricing experiments to users? "
                    "We need to test different pricing tiers without disrupting existing customers."
                ),
                "success_metrics": "95% uptime during experiments, <2% churn increase, 10% conversion lift",
                "constraints": [
                    {"type": "time", "description": "Must be live within 6 weeks", "value": "tight 6 weeks"},
                    {"type": "budget", "description": "Limited budget, no new SaaS tools", "value": "limited budget"},
                    {"type": "technical", "description": "Must use existing infrastructure", "value": "existing infra"},
                ],
                "options": [
                    {
                        "label": "A", "name": "A/B Testing Framework", "order": 0,
                        "description": (
                            "Build a custom A/B testing framework with statistical significance analysis. "
                            "New infrastructure required. Complex architecture with custom build. "
                            "User-facing pricing variants. High engineering effort. Several months of work. "
                            "Significant investment in new team capacity."
                        ),
                    },
                    {
                        "label": "B", "name": "Feature Flags", "order": 1,
                        "description": (
                            "Use an existing feature flag approach with proven, stable patterns. "
                            "Reuse existing infrastructure. Simple, straightforward implementation. "
                            "Quick rollout, already within existing budget, no additional cost. "
                            "User-facing pricing control. Low risk, battle-tested technique. "
                            "Modular, well-documented, maintainable codebase. Aligns with roadmap."
                        ),
                    },
                    {
                        "label": "C", "name": "Manual Rollout", "order": 2,
                        "description": (
                            "Manual process managed by operations team. No additional dev required. "
                            "Free, no license fee, no additional cost. Simple but fragile workaround. "
                            "Technical debt risk. Hard to maintain and scale. Short-term fix only. "
                            "Slow, error-prone, not scalable for user-facing experiments."
                        ),
                    },
                ],
                "weights": {
                    "User Value": 0.20, "Engineering Effort": 0.15, "Time-to-Market": 0.20,
                    "Risk": 0.15, "Cost": 0.10, "Maintainability": 0.10,
                    "Strategic Alignment": 0.05, "Compliance/Privacy": 0.05,
                },
            },
            {
                "title": "Search Upgrade Strategy",
                "problem_statement": (
                    "How should we upgrade our search functionality to improve relevance? "
                    "Current keyword search returns poor results for complex queries."
                ),
                "success_metrics": "20% improvement in search CTR, <200ms p95 latency, NDCG > 0.8",
                "constraints": [
                    {"type": "budget", "description": "Moderate budget available", "value": "moderate"},
                    {"type": "time", "description": "3-month delivery window", "value": "3 months"},
                    {"type": "technical", "description": "Must maintain backward compatibility", "value": "backward compatible"},
                ],
                "options": [
                    {
                        "label": "A", "name": "Keyword Search Enhancement", "order": 0,
                        "description": (
                            "Enhance existing Elasticsearch keyword search with query boosting. "
                            "Proven, stable, existing library, well-documented. Simple approach. "
                            "Quick implementation using existing infrastructure, within budget. "
                            "Low risk, reliable, familiar to the team. Easy to maintain. "
                            "Standard patterns, modular. User-facing search improvement."
                        ),
                    },
                    {
                        "label": "B", "name": "Semantic Search", "order": 1,
                        "description": (
                            "Neural embeddings with vector database for semantic understanding. "
                            "Experimental, unproven at our scale, new technology. "
                            "New infrastructure required, custom build, high engineering effort. "
                            "Several months of research and development, significant investment. "
                            "High risk, volatile, requires new hire with ML expertise. "
                            "Complex architecture, tightly coupled dependencies. User-facing improvement."
                        ),
                    },
                    {
                        "label": "C", "name": "Hybrid Search", "order": 2,
                        "description": (
                            "Combine keyword and semantic search using proven hybrid approach. "
                            "Balanced, modular architecture, standard patterns, well-documented. "
                            "Existing libraries available, manageable cost within budget. "
                            "Reasonable timeline, proven approach reduces risk. "
                            "User experience improvement, customer-centric results. "
                            "Maintainable, structured codebase. Aligns with long-term platform strategy."
                        ),
                    },
                ],
                "weights": {
                    "User Value": 0.25, "Engineering Effort": 0.15, "Time-to-Market": 0.15,
                    "Risk": 0.15, "Cost": 0.10, "Maintainability": 0.10,
                    "Strategic Alignment": 0.05, "Compliance/Privacy": 0.05,
                },
            },
            {
                "title": "Mobile MVP Scope Definition",
                "problem_statement": (
                    "What should be included in our Mobile MVP? "
                    "We need to balance speed-to-market with user experience quality."
                ),
                "success_metrics": "Launch in 8 weeks, >4.0 App Store rating, 40% DAU/MAU ratio",
                "constraints": [
                    {"type": "time", "description": "Must launch in 8 weeks", "value": "tight 8 weeks"},
                    {"type": "budget", "description": "Limited budget, small team", "value": "limited budget"},
                    {"type": "organizational", "description": "Small team of 4 engineers", "value": "small team"},
                ],
                "options": [
                    {
                        "label": "A", "name": "Core Flows Only", "order": 0,
                        "description": (
                            "Authentication, dashboard, and core user journey only. "
                            "Simple, straightforward, existing patterns. Quick to deliver. "
                            "Free of unnecessary features, within existing budget. "
                            "Low risk, proven approach. Maintainable, clean architecture. "
                            "Minimal but functional. Standard implementation. Fast time to market."
                        ),
                    },
                    {
                        "label": "B", "name": "Core + Onboarding", "order": 1,
                        "description": (
                            "Core flows plus an onboarding experience for new users. "
                            "User-facing onboarding, customer-centric experience, user value. "
                            "Existing patterns for core, simple onboarding screens added. "
                            "Manageable scope, within budget, moderate timeline. "
                            "Proven patterns, low risk, reliable implementation. "
                            "Well-documented, maintainable, modular design. "
                            "Aligns with growth strategy and competitive differentiation."
                        ),
                    },
                    {
                        "label": "C", "name": "Full Feature Parity", "order": 2,
                        "description": (
                            "Complete feature parity with the web application. "
                            "Rebuild from scratch, complex architecture, high engineering effort. "
                            "Several months of work, significant investment, expensive. "
                            "High risk, experimental mobile patterns, unproven implementation. "
                            "Requires new hire, extended timeline well beyond 8 weeks. "
                            "Hard to maintain due to large codebase, complex and tightly coupled."
                        ),
                    },
                ],
                "weights": {
                    "User Value": 0.20, "Engineering Effort": 0.20, "Time-to-Market": 0.20,
                    "Risk": 0.15, "Cost": 0.10, "Maintainability": 0.10,
                    "Strategic Alignment": 0.05, "Compliance/Privacy": 0.00,
                },
            },
        ]

        for scenario in scenarios:
            existing = db.query(Decision).filter(
                Decision.workspace_id == ws.id, Decision.title == scenario["title"]
            ).first()
            if existing:
                continue

            d = Decision(
                workspace_id=ws.id, title=scenario["title"],
                problem_statement=scenario["problem_statement"],
                success_metrics=scenario["success_metrics"],
                status="reviewed", created_by=users["pm"].id,
            )
            db.add(d)
            db.flush()

            for c in scenario["constraints"]:
                db.add(Constraint(decision_id=d.id, **c))

            option_objs = []
            for o in scenario["options"]:
                opt = Option(decision_id=d.id, **o)
                db.add(opt)
                db.flush()
                option_objs.append(opt)

            weight_objs = []
            for crit_name, weight in scenario["weights"].items():
                crit = criteria_objs.get(crit_name)
                if crit and weight > 0:
                    w = DecisionCriterionWeight(decision_id=d.id, criterion_id=crit.id, weight=weight)
                    db.add(w)
                    db.flush()
                    weight_objs.append(w)

            db.commit()

            # Run scoring engine
            decision_dict = {
                "id": d.id, "title": d.title,
                "problem_statement": d.problem_statement or "",
                "success_metrics": d.success_metrics or "",
                "constraints": scenario["constraints"],
            }
            options_dicts = [
                {"id": o.id, "label": o.label, "name": o.name, "description": o.description or ""}
                for o in option_objs
            ]
            weights_dicts = [{"criterion_id": w.criterion_id, "weight": w.weight} for w in weight_objs]
            criteria_dicts = [
                {"id": c.id, "name": c.name, "description": c.description or ""}
                for c in criteria_objs.values()
                if any(w.criterion_id == c.id for w in weight_objs)
            ]

            result = scoring_engine.compute_scores(decision_dict, options_dicts, weights_dicts, criteria_dicts)

            ro = ReasoningOutput(
                decision_id=d.id,
                inputs={"decision": decision_dict, "options": options_dicts},
                weights=weights_dicts,
                intermediate_values={"per_option_scores": result["rankings"]},
                option_rankings=result["rankings"],
                narrative=result["narrative"],
                is_llm_assisted=False,
                created_at=datetime.utcnow(),
            )
            db.add(ro)
            db.flush()

            for ranking in result["rankings"]:
                for score in ranking["scores"]:
                    db.add(OptionScore(
                        reasoning_output_id=ro.id, option_id=ranking["option_id"],
                        criterion_id=score["criterion_id"], raw_score=score["raw_score"],
                        weighted_score=score["weighted_score"], explanation=score["explanation"],
                    ))
                db.add(OptionScore(
                    reasoning_output_id=ro.id, option_id=ranking["option_id"],
                    criterion_id=None, raw_score=ranking["total_score"] / 10,
                    weighted_score=ranking["total_score"] / 10,
                    explanation=f"Total: {ranking['total_score']}/100",
                    total_score=ranking["total_score"],
                ))

            db.commit()
            print(f"  ✓ Seeded: {scenario['title']}")
            for r in result["rankings"]:
                print(f"    Rank {r['rank']}: {r['option_name']} ({r['total_score']}/100)")

        print("\nSeed complete! Login credentials:")
        print("  admin@example.com  / Admin123!")
        print("  pm@example.com     / PM123!")
        print("  viewer@example.com / Viewer123!")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
