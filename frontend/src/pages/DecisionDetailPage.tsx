import React, { useEffect, useState, useCallback } from "react";
import { useParams, Link as RouterLink } from "react-router-dom";
import {
  Box, Typography, Button, Tabs, Tab, CircularProgress, Alert, Chip, Breadcrumbs, Link,
  TextField, Card, CardContent, Grid, IconButton, Paper, Divider, Tooltip, Select,
  MenuItem, FormControl, InputLabel, Slider,
} from "@mui/material";
import {
  PlayArrow as EvaluateIcon, Add as AddIcon, Delete as DeleteIcon, Save as SaveIcon,
  History as HistoryIcon, Chat as ChatIcon,
} from "@mui/icons-material";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartTooltip,
  Legend, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis,
} from "recharts";
import { decisionApi, optionApi, constraintApi, criteriaApi, evaluateApi, commentApi } from "../api/endpoints";
import {
  Decision, Option, Constraint, Criterion, Weight, EvaluateResponse, Comment, DecisionVersion,
} from "../api/types";

const MEDAL: Record<number, string> = { 1: "🥇", 2: "🥈", 3: "🥉" };
const STATUS_OPTIONS = ["draft", "reviewed", "approved"];

export function DecisionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const decisionId = Number(id);

  const [decision, setDecision] = useState<Decision | null>(null);
  const [options, setOptions] = useState<Option[]>([]);
  const [constraints, setConstraints] = useState<Constraint[]>([]);
  const [criteria, setCriteria] = useState<Criterion[]>([]);
  const [weights, setWeights] = useState<Weight[]>([]);
  const [evaluation, setEvaluation] = useState<EvaluateResponse | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [versions, setVersions] = useState<DecisionVersion[]>([]);

  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Edit states
  const [editTitle, setEditTitle] = useState("");
  const [editProblem, setEditProblem] = useState("");
  const [editMetrics, setEditMetrics] = useState("");
  const [editStatus, setEditStatus] = useState("");
  const [newComment, setNewComment] = useState("");

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const [dRes, optRes, conRes, critRes] = await Promise.all([
        decisionApi.get(decisionId),
        optionApi.list(decisionId),
        constraintApi.list(decisionId),
        criteriaApi.list(),
      ]);
      setDecision(dRes.data);
      setOptions(optRes.data);
      setConstraints(conRes.data);
      setCriteria(critRes.data);
      setEditTitle(dRes.data.title);
      setEditProblem(dRes.data.problem_statement || "");
      setEditMetrics(dRes.data.success_metrics || "");
      setEditStatus(dRes.data.status);

      const wRes = await criteriaApi.getWeights(decisionId);
      setWeights(wRes.data);

      // Load existing evaluation
      try {
        const evRes = await evaluateApi.latestEvaluation(decisionId);
        setEvaluation(evRes.data);
      } catch { /* none yet */ }

      const [cmtRes, verRes] = await Promise.all([
        commentApi.list(decisionId),
        decisionApi.versions(decisionId),
      ]);
      setComments(cmtRes.data);
      setVersions(verRes.data);
    } catch {
      setError("Failed to load decision");
    } finally {
      setLoading(false);
    }
  }, [decisionId]);

  useEffect(() => { load(); }, [load]);

  const saveDecision = async () => {
    if (!decision) return;
    await decisionApi.update(decisionId, {
      title: editTitle, problem_statement: editProblem,
      success_metrics: editMetrics, status: editStatus,
    });
    setSuccess("Decision saved!");
    setTimeout(() => setSuccess(""), 3000);
    load();
  };

  const handleEvaluate = async () => {
    setEvaluating(true);
    setError("");
    try {
      const res = await evaluateApi.evaluate(decisionId);
      setEvaluation(res.data);
      setTab(4); // Switch to Results tab
      setSuccess("Evaluation complete!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      setError(err.response?.data?.detail || "Evaluation failed");
    } finally {
      setEvaluating(false);
    }
  };

  // Option management
  const addOption = async () => {
    const label = String.fromCharCode(65 + options.length); // A, B, C...
    const opt = await optionApi.create(decisionId, {
      label, name: `Option ${label}`, description: "", order: options.length,
    });
    setOptions([...options, opt.data]);
  };

  const updateOption = async (idx: number, field: string, value: string) => {
    const opt = options[idx];
    const updated = { ...opt, [field]: value };
    setOptions(options.map((o, i) => (i === idx ? updated as Option : o)));
    await optionApi.update(opt.id, { [field]: value });
  };

  const removeOption = async (opt: Option) => {
    await optionApi.delete(opt.id);
    setOptions(options.filter((o) => o.id !== opt.id));
  };

  // Constraint management
  const addConstraint = async () => {
    const c = await constraintApi.create(decisionId, { type: "technical", description: "New constraint" });
    setConstraints([...constraints, c.data]);
  };

  const updateConstraint = async (idx: number, field: string, value: string) => {
    const c = constraints[idx];
    const updated = { ...c, [field]: value };
    setConstraints(constraints.map((x, i) => (i === idx ? updated as Constraint : x)));
    await constraintApi.update(c.id, { [field]: value });
  };

  const removeConstraint = async (c: Constraint) => {
    await constraintApi.delete(c.id);
    setConstraints(constraints.filter((x) => x.id !== c.id));
  };

  // Weight management
  const updateWeight = (criterionId: number, value: number) => {
    setWeights(weights.map((w) => w.criterion_id === criterionId ? { ...w, weight: value } : w));
  };

  const saveWeights = async () => {
    // Initialize weights for any unset criteria
    const allWeights = criteria.map((c) => {
      const existing = weights.find((w) => w.criterion_id === c.id);
      return { criterion_id: c.id, weight: existing?.weight ?? 0.125 };
    });
    await criteriaApi.setWeights(decisionId, allWeights);
    const res = await criteriaApi.getWeights(decisionId);
    setWeights(res.data);
    setSuccess("Weights saved!");
    setTimeout(() => setSuccess(""), 3000);
  };

  const initWeights = async () => {
    const equal = 1 / criteria.length;
    const allWeights = criteria.map((c) => ({ criterion_id: c.id, weight: equal }));
    await criteriaApi.setWeights(decisionId, allWeights);
    const res = await criteriaApi.getWeights(decisionId);
    setWeights(res.data);
  };

  const postComment = async () => {
    if (!newComment.trim()) return;
    const res = await commentApi.create(decisionId, { content: newComment });
    setComments([...comments, res.data]);
    setNewComment("");
  };

  const deleteComment = async (cId: number) => {
    await commentApi.delete(cId);
    setComments(comments.filter((c) => c.id !== cId));
  };

  if (loading) return <Box display="flex" justifyContent="center" mt={4}><CircularProgress /></Box>;
  if (!decision) return <Alert severity="error">Decision not found</Alert>;

  // Chart data
  const chartData = evaluation?.rankings.map((r) => {
    const row: Record<string, string | number> = { option: r.option_label + ": " + r.option_name };
    r.scores.forEach((s) => { row[s.criterion_name] = s.raw_score; });
    return row;
  }) || [];

  const barData = evaluation?.rankings.map((r) => ({
    name: r.option_name.length > 15 ? r.option_name.substring(0, 15) + "…" : r.option_name,
    "Total Score": r.total_score,
    rank: r.rank,
  })) || [];

  const COLORS = ["#2196f3", "#ff9800", "#f44336", "#4caf50", "#9c27b0"];

  return (
    <Box>
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link component={RouterLink} to="/workspaces" underline="hover">Workspaces</Link>
        <Link component={RouterLink} to={`/workspaces/${decision.workspace_id}`} underline="hover">
          Workspace
        </Link>
        <Typography color="text.primary">{decision.title}</Typography>
      </Breadcrumbs>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
        <Box flex={1} mr={2}>
          <Typography variant="h4" fontWeight="bold">{decision.title}</Typography>
          <Chip label={decision.status} size="small" sx={{ mt: 0.5 }} />
        </Box>
        <Button
          variant="contained" color="success" size="large"
          startIcon={evaluating ? <CircularProgress size={16} color="inherit" /> : <EvaluateIcon />}
          onClick={handleEvaluate} disabled={evaluating}
          sx={{ minWidth: 160 }}
        >
          {evaluating ? "Evaluating…" : "Run Evaluation"}
        </Button>
      </Box>

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
        <Tab label="Overview" />
        <Tab label={`Options (${options.length})`} />
        <Tab label={`Constraints (${constraints.length})`} />
        <Tab label="Criteria Weights" />
        <Tab label={`Results ${evaluation ? "✓" : ""}`} />
        <Tab label={`Comments (${comments.length})`} icon={<ChatIcon />} iconPosition="end" />
        <Tab label={`History (${versions.length})`} icon={<HistoryIcon />} iconPosition="end" />
      </Tabs>

      {/* ── Tab 0: Overview ─────────────────────────────────────────────────── */}
      {tab === 0 && (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <TextField label="Title" value={editTitle} onChange={(e) => setEditTitle(e.target.value)} fullWidth />
          <TextField label="Problem Statement" value={editProblem}
            onChange={(e) => setEditProblem(e.target.value)} fullWidth multiline rows={4}
            placeholder="What decision needs to be made?" />
          <TextField label="Success Metrics" value={editMetrics}
            onChange={(e) => setEditMetrics(e.target.value)} fullWidth multiline rows={3}
            placeholder="How will you measure success?" />
          <FormControl sx={{ maxWidth: 200 }}>
            <InputLabel>Status</InputLabel>
            <Select value={editStatus} label="Status" onChange={(e) => setEditStatus(e.target.value)}>
              {STATUS_OPTIONS.map((s) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
            </Select>
          </FormControl>
          <Button variant="contained" startIcon={<SaveIcon />} onClick={saveDecision} sx={{ alignSelf: "flex-start" }}>
            Save Changes
          </Button>
        </Box>
      )}

      {/* ── Tab 1: Options ──────────────────────────────────────────────────── */}
      {tab === 1 && (
        <Box>
          <Button startIcon={<AddIcon />} variant="outlined" onClick={addOption} sx={{ mb: 2 }}>
            Add Option
          </Button>
          {options.map((opt, idx) => (
            <Card key={opt.id} sx={{ mb: 2 }}>
              <CardContent>
                <Box display="flex" gap={2} mb={1}>
                  <TextField
                    label="Label" value={opt.label} size="small" sx={{ width: 80 }}
                    onChange={(e) => updateOption(idx, "label", e.target.value)}
                  />
                  <TextField
                    label="Name" value={opt.name} size="small" fullWidth
                    onChange={(e) => updateOption(idx, "name", e.target.value)}
                  />
                  <Tooltip title="Remove option">
                    <IconButton color="error" onClick={() => removeOption(opt)}><DeleteIcon /></IconButton>
                  </Tooltip>
                </Box>
                <TextField
                  label="Description" value={opt.description || ""} multiline rows={3} fullWidth
                  size="small" placeholder="Describe this option in detail. Include keywords that reflect its nature (e.g., 'proven', 'existing', 'experimental', 'custom build')."
                  onChange={(e) => updateOption(idx, "description", e.target.value)}
                />
              </CardContent>
            </Card>
          ))}
          {options.length === 0 && (
            <Alert severity="info">Add at least 2 options to compare them with the evaluation engine.</Alert>
          )}
        </Box>
      )}

      {/* ── Tab 2: Constraints ──────────────────────────────────────────────── */}
      {tab === 2 && (
        <Box>
          <Button startIcon={<AddIcon />} variant="outlined" onClick={addConstraint} sx={{ mb: 2 }}>
            Add Constraint
          </Button>
          {constraints.map((c, idx) => (
            <Card key={c.id} sx={{ mb: 2 }}>
              <CardContent>
                <Box display="flex" gap={2}>
                  <FormControl size="small" sx={{ width: 160 }}>
                    <InputLabel>Type</InputLabel>
                    <Select value={c.type} label="Type" onChange={(e) => updateConstraint(idx, "type", e.target.value)}>
                      {["time", "budget", "technical", "organizational"].map((t) => (
                        <MenuItem key={t} value={t}>{t}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <TextField
                    label="Description" value={c.description} size="small" fullWidth
                    onChange={(e) => updateConstraint(idx, "description", e.target.value)}
                  />
                  <TextField
                    label="Value" value={c.value || ""} size="small" sx={{ width: 160 }}
                    onChange={(e) => updateConstraint(idx, "value", e.target.value)}
                    placeholder="e.g. 6 weeks"
                  />
                  <IconButton color="error" onClick={() => removeConstraint(c)}><DeleteIcon /></IconButton>
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {/* ── Tab 3: Criteria Weights ─────────────────────────────────────────── */}
      {tab === 3 && (
        <Box>
          <Box display="flex" gap={2} mb={2}>
            <Button variant="outlined" onClick={initWeights}>Reset to Equal Weights</Button>
            <Button variant="contained" startIcon={<SaveIcon />} onClick={saveWeights}>Save Weights</Button>
          </Box>
          <Alert severity="info" sx={{ mb: 2 }}>
            Weights will be normalised automatically. Higher weight = more important criterion.
          </Alert>
          {criteria.map((c) => {
            const w = weights.find((x) => x.criterion_id === c.id);
            const val = w?.weight ?? 0.125;
            return (
              <Box key={c.id} sx={{ mb: 2, p: 2, border: 1, borderColor: "divider", borderRadius: 1 }}>
                <Box display="flex" justifyContent="space-between" mb={0.5}>
                  <Box>
                    <Typography fontWeight="bold">{c.name}</Typography>
                    <Typography variant="caption" color="text.secondary">{c.description}</Typography>
                  </Box>
                  <Typography fontWeight="bold" color="primary">{(val * 100).toFixed(0)}%</Typography>
                </Box>
                <Slider
                  value={val} min={0} max={1} step={0.01}
                  onChange={(_, v) => updateWeight(c.id, v as number)}
                  marks={[{ value: 0, label: "0" }, { value: 0.5, label: "50%" }, { value: 1, label: "100%" }]}
                />
              </Box>
            );
          })}
        </Box>
      )}

      {/* ── Tab 4: Results ──────────────────────────────────────────────────── */}
      {tab === 4 && (
        <Box>
          {!evaluation ? (
            <Alert severity="info">
              No evaluation yet. Click "Run Evaluation" to analyse options.
            </Alert>
          ) : (
            <Box>
              {evaluation.is_llm_assisted && (
                <Chip label="🤖 LLM-assisted text" color="info" size="small" sx={{ mb: 2 }} />
              )}

              {/* Rankings */}
              <Typography variant="h6" fontWeight="bold" gutterBottom>Rankings</Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                {evaluation.rankings.map((r) => (
                  <Grid item xs={12} md={4} key={r.option_id}>
                    <Card sx={{ border: r.rank === 1 ? "2px solid #2196f3" : undefined }}>
                      <CardContent>
                        <Typography variant="h5">{MEDAL[r.rank] || `#${r.rank}`}</Typography>
                        <Typography variant="h6" fontWeight="bold">{r.option_name}</Typography>
                        <Typography variant="h4" color="primary">{r.total_score}/100</Typography>
                        <Divider sx={{ my: 1 }} />
                        {r.risks.slice(0, 2).map((risk, i) => (
                          <Typography key={i} variant="caption" display="block" color="warning.main">
                            ⚠️ {risk}
                          </Typography>
                        ))}
                        {r.recommendations.slice(0, 1).map((rec, i) => (
                          <Typography key={i} variant="caption" display="block" color="success.main">
                            ✓ {rec}
                          </Typography>
                        ))}
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              {/* Bar Chart */}
              <Typography variant="h6" fontWeight="bold" gutterBottom>Score Comparison</Typography>
              <Paper sx={{ p: 2, mb: 3 }}>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={barData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} />
                    <RechartTooltip />
                    <Bar dataKey="Total Score" fill="#2196f3" />
                  </BarChart>
                </ResponsiveContainer>
              </Paper>

              {/* Criterion breakdown */}
              <Typography variant="h6" fontWeight="bold" gutterBottom>Criterion Breakdown</Typography>
              <Paper sx={{ p: 2, mb: 3 }}>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={chartData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" domain={[0, 10]} />
                    <YAxis dataKey="option" type="category" width={120} tick={{ fontSize: 11 }} />
                    <RechartTooltip />
                    <Legend />
                    {evaluation.rankings[0]?.scores.map((s, i) => (
                      <Bar key={s.criterion_name} dataKey={s.criterion_name} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              </Paper>

              {/* Per-option score table */}
              <Typography variant="h6" fontWeight="bold" gutterBottom>Detailed Scores & Explanations</Typography>
              {evaluation.rankings.map((r) => (
                <Card key={r.option_id} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {MEDAL[r.rank]} {r.option_name} — {r.total_score}/100
                    </Typography>
                    <Divider sx={{ my: 1 }} />
                    {r.scores.map((s) => (
                      <Box key={s.criterion_id} sx={{ mb: 1 }}>
                        <Box display="flex" justifyContent="space-between">
                          <Typography variant="body2" fontWeight="bold">{s.criterion_name}</Typography>
                          <Typography variant="body2" color="primary">{s.raw_score}/10</Typography>
                        </Box>
                        <Typography variant="caption" color="text.secondary">{s.explanation}</Typography>
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              ))}

              {/* Narrative */}
              <Typography variant="h6" fontWeight="bold" gutterBottom>Analysis Narrative</Typography>
              <Paper sx={{ p: 2, bgcolor: "grey.50" }}>
                <Typography variant="body2" sx={{ whiteSpace: "pre-wrap", fontFamily: "monospace", fontSize: "0.85rem" }}>
                  {evaluation.narrative}
                </Typography>
              </Paper>
            </Box>
          )}
        </Box>
      )}

      {/* ── Tab 5: Comments ─────────────────────────────────────────────────── */}
      {tab === 5 && (
        <Box>
          <Box display="flex" gap={1} mb={2}>
            <TextField
              value={newComment} onChange={(e) => setNewComment(e.target.value)}
              placeholder="Add a comment…" fullWidth size="small" multiline rows={2}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); postComment(); } }}
            />
            <Button variant="contained" onClick={postComment} sx={{ alignSelf: "flex-start" }}>Post</Button>
          </Box>
          {comments.map((c) => (
            <Card key={c.id} sx={{ mb: 1 }}>
              <CardContent sx={{ py: 1 }}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="caption" color="text.secondary">
                    User #{c.author_id} · {new Date(c.created_at).toLocaleString()}
                  </Typography>
                  <IconButton size="small" color="error" onClick={() => deleteComment(c.id)}>
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Box>
                <Typography variant="body2">{c.content}</Typography>
              </CardContent>
            </Card>
          ))}
          {comments.length === 0 && (
            <Typography color="text.secondary" align="center" sx={{ mt: 4 }}>No comments yet.</Typography>
          )}
        </Box>
      )}

      {/* ── Tab 6: History ──────────────────────────────────────────────────── */}
      {tab === 6 && (
        <Box>
          {versions.length === 0 ? (
            <Alert severity="info">No version history yet. Make changes and save to create versions.</Alert>
          ) : (
            versions.map((v) => (
              <Card key={v.id} sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="subtitle2" fontWeight="bold">
                    Version {v.version_number} — {new Date(v.created_at).toLocaleString()}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">By user #{v.created_by}</Typography>
                  {v.snapshot && (
                    <Box sx={{ mt: 1, p: 1, bgcolor: "grey.100", borderRadius: 1 }}>
                      <Typography variant="caption" component="pre" sx={{ fontFamily: "monospace" }}>
                        {JSON.stringify(v.snapshot, null, 2)}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </Box>
      )}
    </Box>
  );
}
