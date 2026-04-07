import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { MemoryRouter } from "react-router-dom";

// ── Mock API calls ──────────────────────────────────────────────────────────
vi.mock("../api/endpoints", () => ({
  authApi: {
    me: vi.fn().mockResolvedValue({ data: { id: 1, email: "test@example.com", username: "tester", is_active: true, roles: ["pm"] } }),
    login: vi.fn(),
    register: vi.fn(),
  },
  workspaceApi: {
    list: vi.fn().mockResolvedValue({ data: [] }),
    get: vi.fn().mockResolvedValue({ data: { id: 1, name: "WS", description: "", goals: "", context: "", owner_id: 1, created_at: new Date().toISOString(), updated_at: new Date().toISOString() } }),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
  decisionApi: {
    list: vi.fn().mockResolvedValue({ data: [] }),
    get: vi.fn().mockResolvedValue({ data: { id: 1, workspace_id: 1, title: "Test Decision", problem_statement: "A test problem", success_metrics: "Fast", status: "draft", created_by: 1, created_at: new Date().toISOString(), updated_at: new Date().toISOString() } }),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    versions: vi.fn().mockResolvedValue({ data: [] }),
  },
  optionApi: { list: vi.fn().mockResolvedValue({ data: [] }), create: vi.fn(), update: vi.fn(), delete: vi.fn() },
  constraintApi: { list: vi.fn().mockResolvedValue({ data: [] }), create: vi.fn(), update: vi.fn(), delete: vi.fn() },
  criteriaApi: {
    list: vi.fn().mockResolvedValue({ data: [
      { id: 1, name: "User Value", description: "Value to users", is_global: true },
      { id: 2, name: "Engineering Effort", description: "Effort", is_global: true },
    ] }),
    getWeights: vi.fn().mockResolvedValue({ data: [] }),
    setWeights: vi.fn().mockResolvedValue({ data: [] }),
  },
  evaluateApi: { evaluate: vi.fn(), latestEvaluation: vi.fn().mockRejectedValue({ response: { status: 404 } }) },
  commentApi: { list: vi.fn().mockResolvedValue({ data: [] }), create: vi.fn(), update: vi.fn(), delete: vi.fn() },
  prioritizeApi: { prioritize: vi.fn().mockResolvedValue({ data: { items: [] } }) },
  auditApi: { list: vi.fn().mockResolvedValue({ data: [] }) },
}));

// ── Mock AuthContext ──────────────────────────────────────────────────────────
vi.mock("../contexts/AuthContext", () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useAuth: () => ({
    user: { id: 1, email: "test@example.com", username: "tester", is_active: true, roles: ["pm"] },
    token: "fake-token",
    login: vi.fn(),
    logout: vi.fn(),
    loading: false,
  }),
}));

import { WorkspacesPage } from "../pages/WorkspacesPage";
import { PrioritizePage } from "../pages/PrioritizePage";
import { SettingsPage } from "../pages/SettingsPage";
import { LoginPage } from "../pages/LoginPage";

function wrap(ui: React.ReactElement, route = "/") {
  return render(<MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>);
}

// ── LoginPage ────────────────────────────────────────────────────────────────
describe("LoginPage", () => {
  it("renders sign in and register tabs", () => {
    wrap(<LoginPage />);
    expect(screen.getAllByText("Sign In").length).toBeGreaterThan(0);
    expect(screen.getByText("Register")).toBeInTheDocument();
  });

  it("renders platform title", () => {
    wrap(<LoginPage />);
    expect(screen.getByText("Decision Intelligence")).toBeInTheDocument();
  });

  it("shows demo credentials hint", () => {
    wrap(<LoginPage />);
    expect(screen.getByText(/admin@example.com/i)).toBeInTheDocument();
  });
});

// ── WorkspacesPage ───────────────────────────────────────────────────────────
describe("WorkspacesPage", () => {
  it("renders workspaces heading", async () => {
    wrap(<WorkspacesPage />);
    await waitFor(() => expect(screen.getByText("Workspaces")).toBeInTheDocument());
  });

  it("shows New Workspace button", async () => {
    wrap(<WorkspacesPage />);
    await waitFor(() => expect(screen.getByText("New Workspace")).toBeInTheDocument());
  });

  it("shows empty state when no workspaces", async () => {
    wrap(<WorkspacesPage />);
    await waitFor(() => expect(screen.getByText("No workspaces yet")).toBeInTheDocument());
  });
});

// ── SettingsPage ─────────────────────────────────────────────────────────────
describe("SettingsPage", () => {
  it("renders settings heading", async () => {
    wrap(<SettingsPage />);
    await waitFor(() => expect(screen.getByText("Settings")).toBeInTheDocument());
  });

  it("shows LLM integration section after loading", async () => {
    wrap(<SettingsPage />);
    await screen.findByText("LLM Integration");
    expect(screen.getByText("LLM Integration")).toBeInTheDocument();
  });

  it("shows criteria weight templates", async () => {
    wrap(<SettingsPage />);
    await screen.findByText("Criteria Weight Templates");
    expect(screen.getByText("MVP Features")).toBeInTheDocument();
  });

  it("shows account section with user info", async () => {
    wrap(<SettingsPage />);
    await waitFor(() => expect(screen.getByText("Account")).toBeInTheDocument());
  });
});

// ── PrioritizePage ───────────────────────────────────────────────────────────
describe("PrioritizePage", () => {
  it("renders prioritization heading", async () => {
    wrap(<PrioritizePage />);
    await waitFor(() => expect(screen.getByText("Prioritization Dashboard")).toBeInTheDocument());
  });

  it("shows prioritize button after loading", async () => {
    wrap(<PrioritizePage />);
    await waitFor(() => {
      const btn = screen.getByRole("button", { name: /prioritize/i });
      expect(btn).toBeInTheDocument();
    });
  });
});
