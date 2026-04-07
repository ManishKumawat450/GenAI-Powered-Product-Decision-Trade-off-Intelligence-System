import api from "./client";

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: { email: string; username: string; password: string; role?: string }) =>
    api.post("/auth/register", data),
  login: (data: { email: string; password: string }) => api.post("/auth/login", data),
  me: () => api.get("/auth/me"),
};

// ── Workspaces ────────────────────────────────────────────────────────────────
export const workspaceApi = {
  list: () => api.get("/workspaces"),
  create: (data: { name: string; description?: string; goals?: string; context?: string }) =>
    api.post("/workspaces", data),
  get: (id: number) => api.get(`/workspaces/${id}`),
  update: (id: number, data: Partial<{ name: string; description: string; goals: string; context: string }>) =>
    api.put(`/workspaces/${id}`, data),
  delete: (id: number) => api.delete(`/workspaces/${id}`),
};

// ── Decisions ─────────────────────────────────────────────────────────────────
export const decisionApi = {
  list: (workspaceId: number) => api.get(`/workspaces/${workspaceId}/decisions`),
  create: (workspaceId: number, data: { title: string; problem_statement?: string; success_metrics?: string }) =>
    api.post(`/workspaces/${workspaceId}/decisions`, data),
  get: (id: number) => api.get(`/decisions/${id}`),
  update: (id: number, data: Partial<{ title: string; problem_statement: string; success_metrics: string; status: string }>) =>
    api.put(`/decisions/${id}`, data),
  delete: (id: number) => api.delete(`/decisions/${id}`),
  versions: (id: number) => api.get(`/decisions/${id}/versions`),
};

// ── Options ───────────────────────────────────────────────────────────────────
export const optionApi = {
  list: (decisionId: number) => api.get(`/decisions/${decisionId}/options`),
  create: (decisionId: number, data: { label: string; name: string; description?: string; order?: number }) =>
    api.post(`/decisions/${decisionId}/options`, data),
  update: (id: number, data: Partial<{ label: string; name: string; description: string; order: number }>) =>
    api.put(`/options/${id}`, data),
  delete: (id: number) => api.delete(`/options/${id}`),
};

// ── Constraints ───────────────────────────────────────────────────────────────
export const constraintApi = {
  list: (decisionId: number) => api.get(`/decisions/${decisionId}/constraints`),
  create: (decisionId: number, data: { type: string; description: string; value?: string }) =>
    api.post(`/decisions/${decisionId}/constraints`, data),
  update: (id: number, data: Partial<{ type: string; description: string; value: string }>) =>
    api.put(`/constraints/${id}`, data),
  delete: (id: number) => api.delete(`/constraints/${id}`),
};

// ── Criteria & Weights ────────────────────────────────────────────────────────
export const criteriaApi = {
  list: () => api.get("/criteria"),
  getWeights: (decisionId: number) => api.get(`/decisions/${decisionId}/weights`),
  setWeights: (decisionId: number, weights: { criterion_id: number; weight: number }[]) =>
    api.put(`/decisions/${decisionId}/weights`, { weights }),
};

// ── Evaluate ──────────────────────────────────────────────────────────────────
export const evaluateApi = {
  evaluate: (decisionId: number) => api.post(`/decisions/${decisionId}/evaluate`),
  latestEvaluation: (decisionId: number) => api.get(`/decisions/${decisionId}/latest-evaluation`),
};

// ── Comments ──────────────────────────────────────────────────────────────────
export const commentApi = {
  list: (decisionId: number) => api.get(`/decisions/${decisionId}/comments`),
  create: (decisionId: number, data: { content: string; option_id?: number }) =>
    api.post(`/decisions/${decisionId}/comments`, data),
  update: (id: number, content: string) => api.put(`/comments/${id}`, { content }),
  delete: (id: number) => api.delete(`/comments/${id}`),
};

// ── Prioritize ────────────────────────────────────────────────────────────────
export const prioritizeApi = {
  prioritize: (decision_ids: number[]) => api.post("/prioritize", { decision_ids }),
};

// ── Audit ─────────────────────────────────────────────────────────────────────
export const auditApi = {
  list: (skip = 0, limit = 50) => api.get(`/audit?skip=${skip}&limit=${limit}`),
};
