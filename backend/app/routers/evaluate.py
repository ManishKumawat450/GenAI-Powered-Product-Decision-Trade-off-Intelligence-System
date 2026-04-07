from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.decision import Decision, Constraint, Option, ReasoningOutput
from app.models.criteria import Criterion, DecisionCriterionWeight, OptionScore
from app.models.collaboration import AuditLog
from app.schemas.scoring import EvaluateResponse, OptionRankingOut, OptionCriterionScore
from app.core.deps import get_current_user
from app.core.scoring_engine import scoring_engine

router = APIRouter(tags=["Evaluate"])


@router.post("/decisions/{decision_id}/evaluate", response_model=EvaluateResponse)
def evaluate_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    options = db.query(Option).filter(Option.decision_id == decision_id).order_by(Option.order).all()
    if not options:
        raise HTTPException(status_code=400, detail="Decision has no options to evaluate")

    criteria_weights = db.query(DecisionCriterionWeight).filter(
        DecisionCriterionWeight.decision_id == decision_id
    ).all()
    if not criteria_weights:
        raise HTTPException(status_code=400, detail="No criteria weights set for this decision")

    criteria_ids = [w.criterion_id for w in criteria_weights]
    criteria = db.query(Criterion).filter(Criterion.id.in_(criteria_ids)).all()

    constraints = db.query(Constraint).filter(Constraint.decision_id == decision_id).all()

    # Build plain dicts for the engine
    decision_dict = {
        "id": decision.id,
        "title": decision.title,
        "problem_statement": decision.problem_statement or "",
        "success_metrics": decision.success_metrics or "",
        "constraints": [
            {"type": c.type, "description": c.description, "value": c.value}
            for c in constraints
        ],
    }
    options_dicts = [
        {"id": o.id, "label": o.label, "name": o.name, "description": o.description or ""}
        for o in options
    ]
    weights_dicts = [
        {"criterion_id": w.criterion_id, "weight": w.weight} for w in criteria_weights
    ]
    criteria_dicts = [
        {"id": c.id, "name": c.name, "description": c.description or ""} for c in criteria
    ]

    result = scoring_engine.compute_scores(decision_dict, options_dicts, weights_dicts, criteria_dicts)

    # Persist reasoning output
    ro = ReasoningOutput(
        decision_id=decision_id,
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

    # Persist option scores
    for ranking in result["rankings"]:
        for score in ranking["scores"]:
            os_row = OptionScore(
                reasoning_output_id=ro.id,
                option_id=ranking["option_id"],
                criterion_id=score["criterion_id"],
                raw_score=score["raw_score"],
                weighted_score=score["weighted_score"],
                explanation=score["explanation"],
            )
            db.add(os_row)
        # Total score row (criterion_id=None)
        os_total = OptionScore(
            reasoning_output_id=ro.id,
            option_id=ranking["option_id"],
            criterion_id=None,
            raw_score=ranking["total_score"] / 10,
            weighted_score=ranking["total_score"] / 10,
            explanation=f"Total weighted score: {ranking['total_score']}/100",
            total_score=ranking["total_score"],
        )
        db.add(os_total)

    db.commit()
    db.refresh(ro)

    # Audit log
    db.add(AuditLog(user_id=current_user.id, action="evaluate", resource_type="decision",
                    resource_id=decision_id, timestamp=datetime.utcnow()))
    db.commit()

    # Build response
    rankings_out = []
    for r in result["rankings"]:
        scores_out = [
            OptionCriterionScore(
                criterion_id=s["criterion_id"], criterion_name=s["criterion_name"],
                raw_score=s["raw_score"], weighted_score=s["weighted_score"],
                explanation=s["explanation"],
            )
            for s in r["scores"]
        ]
        rankings_out.append(OptionRankingOut(
            option_id=r["option_id"], option_label=r["option_label"], option_name=r["option_name"],
            rank=r["rank"], total_score=r["total_score"], scores=scores_out,
            risks=r["risks"], recommendations=r["recommendations"],
        ))

    return EvaluateResponse(
        decision_id=decision_id,
        reasoning_output_id=ro.id,
        rankings=rankings_out,
        narrative=result["narrative"],
        trade_off_matrix=result["trade_off_matrix"],
        is_llm_assisted=ro.is_llm_assisted,
        created_at=ro.created_at,
    )


@router.get("/decisions/{decision_id}/latest-evaluation", response_model=EvaluateResponse)
def latest_evaluation(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ro = db.query(ReasoningOutput).filter(ReasoningOutput.decision_id == decision_id)\
        .order_by(ReasoningOutput.created_at.desc()).first()
    if not ro:
        raise HTTPException(status_code=404, detail="No evaluation found for this decision")

    rankings_out = []
    for r in (ro.option_rankings or []):
        scores_out = [
            OptionCriterionScore(**{k: s[k] for k in ["criterion_id", "criterion_name", "raw_score", "weighted_score", "explanation"]})
            for s in r.get("scores", [])
        ]
        rankings_out.append(OptionRankingOut(
            option_id=r["option_id"], option_label=r["option_label"], option_name=r["option_name"],
            rank=r["rank"], total_score=r["total_score"], scores=scores_out,
            risks=r.get("risks", []), recommendations=r.get("recommendations", []),
        ))

    return EvaluateResponse(
        decision_id=decision_id,
        reasoning_output_id=ro.id,
        rankings=rankings_out,
        narrative=ro.narrative or "",
        trade_off_matrix=ro.intermediate_values.get("trade_off_matrix", []) if ro.intermediate_values else [],
        is_llm_assisted=ro.is_llm_assisted,
        created_at=ro.created_at,
    )
