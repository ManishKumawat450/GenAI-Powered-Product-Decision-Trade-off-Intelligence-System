from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    problem_statement = Column(Text)
    success_metrics = Column(Text)
    status = Column(String(50), default="draft", nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    workspace = relationship("Workspace", back_populates="decisions")
    constraints = relationship("Constraint", back_populates="decision", cascade="all, delete-orphan")
    options = relationship("Option", back_populates="decision", cascade="all, delete-orphan")
    criteria_weights = relationship("DecisionCriterionWeight", back_populates="decision", cascade="all, delete-orphan")
    reasoning_outputs = relationship("ReasoningOutput", back_populates="decision", cascade="all, delete-orphan")
    versions = relationship("DecisionVersion", back_populates="decision", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="decision", cascade="all, delete-orphan")


class Constraint(Base):
    __tablename__ = "constraints"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    value = Column(String(255))

    decision = relationship("Decision", back_populates="constraints")


class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    order = Column(Integer, default=0, nullable=False)

    decision = relationship("Decision", back_populates="options")
    scores = relationship("OptionScore", back_populates="option", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="option")


class DecisionVersion(Base):
    __tablename__ = "decision_versions"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    snapshot = Column(JSON)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    decision = relationship("Decision", back_populates="versions")


class ReasoningOutput(Base):
    __tablename__ = "reasoning_outputs"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id", ondelete="CASCADE"), nullable=False)
    inputs = Column(JSON)
    weights = Column(JSON)
    intermediate_values = Column(JSON)
    option_rankings = Column(JSON)
    narrative = Column(Text)
    is_llm_assisted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    decision = relationship("Decision", back_populates="reasoning_outputs")
    option_scores = relationship("OptionScore", back_populates="reasoning_output", cascade="all, delete-orphan")
