export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  roles: string[];
}

export interface Workspace {
  id: number;
  name: string;
  description?: string;
  goals?: string;
  context?: string;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface Decision {
  id: number;
  workspace_id: number;
  title: string;
  problem_statement?: string;
  success_metrics?: string;
  status: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface Option {
  id: number;
  decision_id: number;
  label: string;
  name: string;
  description?: string;
  order: number;
}

export interface Constraint {
  id: number;
  decision_id: number;
  type: string;
  description: string;
  value?: string;
}

export interface Criterion {
  id: number;
  name: string;
  description?: string;
  is_global: boolean;
}

export interface Weight {
  id: number;
  decision_id: number;
  criterion_id: number;
  criterion_name: string;
  weight: number;
}

export interface OptionCriterionScore {
  criterion_id: number;
  criterion_name: string;
  raw_score: number;
  weighted_score: number;
  explanation: string;
}

export interface OptionRanking {
  option_id: number;
  option_label: string;
  option_name: string;
  rank: number;
  total_score: number;
  scores: OptionCriterionScore[];
  risks: string[];
  recommendations: string[];
}

export interface EvaluateResponse {
  decision_id: number;
  reasoning_output_id: number;
  rankings: OptionRanking[];
  narrative: string;
  trade_off_matrix: Record<string, number | string>[];
  is_llm_assisted: boolean;
  created_at: string;
}

export interface Comment {
  id: number;
  decision_id: number;
  option_id?: number;
  author_id: number;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface DecisionVersion {
  id: number;
  decision_id: number;
  version_number: number;
  snapshot?: Record<string, unknown>;
  created_by: number;
  created_at: string;
}

export interface PrioritizeItem {
  decision_id: number;
  decision_title: string;
  rank: number;
  total_score: number;
  impact: number;
  effort: number;
  summary: string;
}

export interface AuditLog {
  id: number;
  user_id?: number;
  action: string;
  resource_type?: string;
  resource_id?: number;
  details?: Record<string, unknown>;
  timestamp: string;
}
