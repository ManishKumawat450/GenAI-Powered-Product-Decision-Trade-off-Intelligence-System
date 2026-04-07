from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, workspaces, decisions, options, constraints, criteria, evaluate, comments, prioritize, audit

app = FastAPI(
    title="GenAI Product Decision Intelligence System",
    description="Structured, explainable decision logic for product trade-offs",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(workspaces.router)
app.include_router(decisions.router)
app.include_router(options.router)
app.include_router(constraints.router)
app.include_router(criteria.router)
app.include_router(evaluate.router)
app.include_router(comments.router)
app.include_router(prioritize.router)
app.include_router(audit.router)


@app.get("/")
def root():
    return {"message": "GenAI Product Decision Intelligence System API", "docs": "/docs"}
