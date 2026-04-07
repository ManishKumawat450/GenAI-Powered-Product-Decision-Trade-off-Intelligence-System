import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box, Typography, Button, Card, CardContent, Grid, CircularProgress, Alert,
  Chip, Paper, Divider, TextField, Autocomplete, Table, TableBody,
  TableCell, TableHead, TableRow,
} from "@mui/material";
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine,
} from "recharts";
import { workspaceApi, decisionApi, prioritizeApi } from "../api/endpoints";
import { Workspace, Decision, PrioritizeItem } from "../api/types";

const COLORS = ["#2196f3", "#ff9800", "#4caf50", "#f44336", "#9c27b0", "#00bcd4"];
const MEDAL: Record<number, string> = { 1: "🥇", 2: "🥈", 3: "🥉" };

export function PrioritizePage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [allDecisions, setAllDecisions] = useState<Decision[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [results, setResults] = useState<PrioritizeItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const load = async () => {
      try {
        const wsRes = await workspaceApi.list();
        setWorkspaces(wsRes.data);
        const decisionLists = await Promise.all(
          wsRes.data.map((ws: Workspace) => decisionApi.list(ws.id))
        );
        const all = decisionLists.flatMap((r) => r.data);
        setAllDecisions(all);
        setSelectedIds(all.map((d: Decision) => d.id));
      } catch {
        setError("Failed to load decisions");
      } finally {
        setInitialLoading(false);
      }
    };
    load();
  }, []);

  const handlePrioritize = async () => {
    if (selectedIds.length === 0) return;
    setLoading(true);
    setError("");
    try {
      const res = await prioritizeApi.prioritize(selectedIds);
      setResults(res.data.items);
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      setError(err.response?.data?.detail || "Prioritization failed");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "prioritization-results.json";
    a.click();
  };

  const scatterData = results.map((r, i) => ({
    x: r.effort, y: r.impact, name: r.decision_title, rank: r.rank,
    total_score: r.total_score, color: COLORS[i % COLORS.length],
  }));

  if (initialLoading) return <Box display="flex" justifyContent="center" mt={4}><CircularProgress /></Box>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold">Prioritization Dashboard</Typography>
          <Typography variant="body2" color="text.secondary">
            Compare and rank multiple decisions by weighted score, impact, and effort
          </Typography>
        </Box>
        {results.length > 0 && (
          <Button variant="outlined" onClick={handleExport}>Export JSON</Button>
        )}
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          Select Decisions to Prioritize
        </Typography>
        <Autocomplete
          multiple value={allDecisions.filter((d) => selectedIds.includes(d.id))}
          options={allDecisions}
          getOptionLabel={(d) => d.title}
          onChange={(_, val) => setSelectedIds(val.map((d) => d.id))}
          renderInput={(params) => <TextField {...params} label="Decisions" placeholder="Select decisions…" />}
          sx={{ mb: 2 }}
        />
        <Button
          variant="contained" size="large" onClick={handlePrioritize}
          disabled={loading || selectedIds.length === 0}
        >
          {loading ? <CircularProgress size={20} /> : `Prioritize ${selectedIds.length} Decision${selectedIds.length !== 1 ? "s" : ""}`}
        </Button>
      </Paper>

      {results.length > 0 && (
        <>
          {/* Impact vs Effort Quadrant */}
          <Typography variant="h6" fontWeight="bold" gutterBottom>
            Impact vs. Effort Quadrant
          </Typography>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
              X-axis = Effort (higher = more effort), Y-axis = Impact (higher = more impact)
            </Typography>
            <Box sx={{ position: "relative" }}>
              <Box sx={{ position: "absolute", top: "10%", right: "5%", color: "success.main", fontSize: "0.7rem" }}>
                ★ Quick Wins
              </Box>
              <Box sx={{ position: "absolute", top: "10%", left: "5%", color: "warning.main", fontSize: "0.7rem" }}>
                ● Major Projects
              </Box>
              <Box sx={{ position: "absolute", bottom: "5%", right: "5%", color: "info.main", fontSize: "0.7rem" }}>
                ◦ Fill-ins
              </Box>
              <Box sx={{ position: "absolute", bottom: "5%", left: "5%", color: "error.main", fontSize: "0.7rem" }}>
                ✗ Thankless Tasks
              </Box>
            </Box>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="x" type="number" domain={[0, 11]} name="Effort"
                  label={{ value: "Effort →", position: "bottom" }} />
                <YAxis dataKey="y" type="number" domain={[0, 11]} name="Impact"
                  label={{ value: "Impact →", angle: -90, position: "insideLeft" }} />
                <ReferenceLine x={5.5} stroke="#ccc" strokeDasharray="5 5" />
                <ReferenceLine y={5.5} stroke="#ccc" strokeDasharray="5 5" />
                <Tooltip
                  content={({ payload }) => {
                    if (!payload?.length) return null;
                    const d = payload[0].payload;
                    return (
                      <Paper sx={{ p: 1 }}>
                        <Typography variant="body2" fontWeight="bold">{d.name}</Typography>
                        <Typography variant="caption">Impact: {d.y.toFixed(1)} | Effort: {d.x.toFixed(1)}</Typography>
                        <br />
                        <Typography variant="caption">Score: {d.total_score}/100</Typography>
                      </Paper>
                    );
                  }}
                />
                <Scatter data={scatterData} shape="circle">
                  {scatterData.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </Paper>

          {/* Ranked List */}
          <Typography variant="h6" fontWeight="bold" gutterBottom>Ranked Decisions</Typography>
          <Table component={Paper} sx={{ mb: 3 }}>
            <TableHead>
              <TableRow sx={{ bgcolor: "primary.main" }}>
                <TableCell sx={{ color: "white" }}>Rank</TableCell>
                <TableCell sx={{ color: "white" }}>Decision</TableCell>
                <TableCell sx={{ color: "white" }} align="center">Score</TableCell>
                <TableCell sx={{ color: "white" }} align="center">Impact</TableCell>
                <TableCell sx={{ color: "white" }} align="center">Effort</TableCell>
                <TableCell sx={{ color: "white" }}>Summary</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {results.map((r) => (
                <TableRow key={r.decision_id} hover
                  sx={{ cursor: "pointer" }} onClick={() => navigate(`/decisions/${r.decision_id}`)}>
                  <TableCell>
                    <Typography variant="h6">{MEDAL[r.rank] || `#${r.rank}`}</Typography>
                  </TableCell>
                  <TableCell>
                    <Typography fontWeight="bold">{r.decision_title}</Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Chip label={`${r.total_score}/100`} color={r.total_score >= 70 ? "success" : r.total_score >= 50 ? "warning" : "error"} />
                  </TableCell>
                  <TableCell align="center">{r.impact.toFixed(1)}/10</TableCell>
                  <TableCell align="center">{r.effort.toFixed(1)}/10</TableCell>
                  <TableCell>
                    <Typography variant="caption">{r.summary}</Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <Typography variant="h6" fontWeight="bold" gutterBottom>Suggested Phasing</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Card sx={{ borderTop: "3px solid #4caf50" }}>
                <CardContent>
                  <Typography variant="subtitle1" fontWeight="bold" color="success.main">
                    ✅ MVP Scope (Score ≥ 60)
                  </Typography>
                  {results.filter((r) => r.total_score >= 60).map((r) => (
                    <Typography key={r.decision_id} variant="body2">
                      {MEDAL[r.rank] || `#${r.rank}`} {r.decision_title}
                    </Typography>
                  ))}
                  {results.filter((r) => r.total_score >= 60).length === 0 && (
                    <Typography variant="body2" color="text.secondary">No decisions meet MVP threshold</Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card sx={{ borderTop: "3px solid #ff9800" }}>
                <CardContent>
                  <Typography variant="subtitle1" fontWeight="bold" color="warning.main">
                    🔜 Later Phases (Score &lt; 60)
                  </Typography>
                  {results.filter((r) => r.total_score < 60).map((r) => (
                    <Typography key={r.decision_id} variant="body2">
                      {MEDAL[r.rank] || `#${r.rank}`} {r.decision_title}
                    </Typography>
                  ))}
                  {results.filter((r) => r.total_score < 60).length === 0 && (
                    <Typography variant="body2" color="text.secondary">All decisions meet MVP threshold</Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
}
