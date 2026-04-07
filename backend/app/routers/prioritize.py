from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.decision import Decision, ReasoningOutput, Constraint
from app.models.criteria import Criterion, DecisionCriterionWeight
from app.schemas.scoring import PrioritizeRequest, PrioritizeResponse, PrioritizeItem
from app.core.deps import get_current_user
from app.core.scoring_engine import scoring_engine

router = APIRouter(tags=["Prioritize"])


@router.post("/prioritize", response_model=PrioritizeResponse)
def prioritize(
    payload: PrioritizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = []
    for did in payload.decision_ids:
        decision = db.query(Decision).filter(Decision.id == did).first()
        if not decision:
            continue

        # Try latest evaluation
        ro = db.query(ReasoningOutput).filter(ReasoningOutput.decision_id == did)\
            .order_by(ReasoningOutput.created_at.desc()).first()

        if ro and ro.option_rankings:
            rankings = ro.option_rankings
        else:
            # Run scoring engine on the fly
            from app.models.decision import Option
            options = db.query(Option).filter(Option.decision_id == did).all()
            criteria_weights = db.query(DecisionCriterionWeight).filter(
                DecisionCriterionWeight.decision_id == did).all()
            if not options or not criteria_weights:
                continue
            criteria_ids = [w.criterion_id for w in criteria_weights]
            criteria = db.query(Criterion).filter(Criterion.id.in_(criteria_ids)).all()
            constraints = db.query(Constraint).filter(Constraint.decision_id == did).all()

            decision_dict = {
                "id": decision.id, "title": decision.title,
                "problem_statement": decision.problem_statement or "",
                "success_metrics": decision.success_metrics or "",
                "constraints": [{"type": c.type, "description": c.description, "value": c.value} for c in constraints],
            }
            options_dicts = [{"id": o.id, "label": o.label, "name": o.name, "description": o.description or ""} for o in options]
            weights_dicts = [{"criterion_id": w.criterion_id, "weight": w.weight} for w in criteria_weights]
            criteria_dicts = [{"id": c.id, "name": c.name, "description": c.description or ""} for c in criteria]

            result = scoring_engine.compute_scores(decision_dict, options_dicts, weights_dicts, criteria_dicts)
            rankings = result["rankings"]

        if not rankings:
            continue

        top = rankings[0]
        total_score = top["total_score"]

        # Compute impact and effort from scores
        impact = 5.0
        effort = 5.0
        for s in top.get("scores", []):
            if s["criterion_name"] in ("User Value", "Strategic Alignment"):
                impact = (impact + s["raw_score"]) / 2
            if s["criterion_name"] == "Engineering Effort":
                effort = s["raw_score"]

        summary = top.get("recommendations", [""])[0] if top.get("recommendations") else ""

        items.append(PrioritizeItem(
            decision_id=did,
            decision_title=decision.title,
            rank=0,  # will set after sort
            total_score=total_score,
            impact=round(impact, 2),
            effort=round(effort, 2),
            summary=summary,
        ))

    # Sort by total score
    items.sort(key=lambda x: x.total_score, reverse=True)
    for i, item in enumerate(items):
        item.rank = i + 1

    return PrioritizeResponse(items=items)
