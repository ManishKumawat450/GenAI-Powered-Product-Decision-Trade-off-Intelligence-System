import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models.user import User, Role
from app.models.workspace import Workspace
from app.models.decision import Decision, Option, Constraint
from app.models.criteria import Criterion, DecisionCriterionWeight
from app.core.security import hash_password, create_access_token

DATABASE_URL = "sqlite:///./test_decision.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    conn = engine.connect()
    transaction = conn.begin()
    session = TestingSessionLocal(bind=conn)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        conn.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    role = db.query(Role).filter(Role.name == "admin").first()
    if not role:
        role = Role(name="admin")
        db.add(role)
        db.flush()
    user = User(
        email="test_admin@example.com", username="test_admin",
        hashed_password=hash_password("Admin123!")
    )
    user.roles.append(role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def pm_user(db):
    role = db.query(Role).filter(Role.name == "pm").first()
    if not role:
        role = Role(name="pm")
        db.add(role)
        db.flush()
    user = User(
        email="test_pm@example.com", username="test_pm",
        hashed_password=hash_password("PM123!")
    )
    user.roles.append(role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    return create_access_token({"sub": str(admin_user.id)})


@pytest.fixture
def pm_token(pm_user):
    return create_access_token({"sub": str(pm_user.id)})


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def pm_headers(pm_token):
    return {"Authorization": f"Bearer {pm_token}"}


@pytest.fixture
def workspace(db, admin_user):
    ws = Workspace(
        name="Test Workspace", description="For testing",
        goals="Test goals", context="Test context", owner_id=admin_user.id
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws


@pytest.fixture
def decision(db, workspace, admin_user):
    d = Decision(
        workspace_id=workspace.id, title="Test Decision",
        problem_statement="How to choose?", success_metrics="Fast and cheap",
        status="draft", created_by=admin_user.id
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


@pytest.fixture
def criteria_and_weights(db, decision):
    """Creates criteria and weights for the test decision."""
    criteria_data = [
        ("User Value", "Value to users"),
        ("Engineering Effort", "Dev complexity"),
        ("Time-to-Market", "Speed"),
        ("Risk", "Execution risk"),
    ]
    criteria_objs = []
    for name, desc in criteria_data:
        c = db.query(Criterion).filter(Criterion.name == name).first()
        if not c:
            c = Criterion(name=name, description=desc, is_global=True)
            db.add(c)
            db.flush()
        criteria_objs.append(c)

    for i, c in enumerate(criteria_objs):
        w = DecisionCriterionWeight(decision_id=decision.id, criterion_id=c.id, weight=0.25)
        db.add(w)
    db.commit()
    return criteria_objs


@pytest.fixture
def options(db, decision):
    opts = [
        Option(decision_id=decision.id, label="A", name="Option Alpha",
               description="proven stable existing library simple quick low risk free open source maintainable", order=0),
        Option(decision_id=decision.id, label="B", name="Option Beta",
               description="custom build experimental unproven expensive complex new infrastructure rebuild significant investment", order=1),
    ]
    for o in opts:
        db.add(o)
    db.commit()
    for o in opts:
        db.refresh(o)
    return opts
