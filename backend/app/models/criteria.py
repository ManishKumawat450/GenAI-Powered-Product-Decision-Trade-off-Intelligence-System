from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Criterion(Base):
    __tablename__ = "criteria"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_global = Column(Boolean, default=True, nullable=False)

    weights = relationship("DecisionCriterionWeight", back_populates="criterion")
    option_scores = relationship("OptionScore", back_populates="criterion")


class DecisionCriterionWeight(Base):
    __tablename__ = "decision_criteria_weights"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), nullable=False)
    weight = Column(Float, nullable=False)

    decision = relationship("Decision", back_populates="criteria_weights")
    criterion = relationship("Criterion", back_populates="weights")


class OptionScore(Base):
    __tablename__ = "option_scores"

    id = Column(Integer, primary_key=True, index=True)
    reasoning_output_id = Column(Integer, ForeignKey("reasoning_outputs.id", ondelete="CASCADE"), nullable=False)
    option_id = Column(Integer, ForeignKey("options.id", ondelete="CASCADE"), nullable=False)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), nullable=True)
    raw_score = Column(Float, nullable=False)
    weighted_score = Column(Float, nullable=False)
    explanation = Column(Text)
    total_score = Column(Float, nullable=True)

    reasoning_output = relationship("ReasoningOutput", back_populates="option_scores")
    option = relationship("Option", back_populates="scores")
    criterion = relationship("Criterion", back_populates="option_scores")
