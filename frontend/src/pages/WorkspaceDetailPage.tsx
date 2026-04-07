import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link as RouterLink } from "react-router-dom";
import {
  Box, Typography, Button, Card, CardContent, CardActions, Grid, Chip,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, CircularProgress,
  Alert, Breadcrumbs, Link, IconButton, Tooltip,
} from "@mui/material";
import {
  Add as AddIcon, ArrowBack, Delete as DeleteIcon, Assignment as DecisionIcon,
} from "@mui/icons-material";
import { useForm } from "react-hook-form";
import { workspaceApi, decisionApi } from "../api/endpoints";
import { Workspace, Decision } from "../api/types";

const STATUS_COLORS: Record<string, "default" | "warning" | "success"> = {
  draft: "default", reviewed: "warning", approved: "success",
};

interface DecisionForm { title: string; problem_statement?: string; success_metrics?: string }

export function WorkspaceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const wsId = Number(id);
  const navigate = useNavigate();

  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const { register, handleSubmit, reset } = useForm<DecisionForm>();

  const load = async () => {
    try {
      setLoading(true);
      const [wsRes, decRes] = await Promise.all([
        workspaceApi.get(wsId),
        decisionApi.list(wsId),
      ]);
      setWorkspace(wsRes.data);
      setDecisions(decRes.data);
    } catch {
      setError("Failed to load workspace");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [wsId]);

  const handleCreate = async (data: DecisionForm) => {
    setSubmitting(true);
    try {
      const res = await decisionApi.create(wsId, data);
      reset();
      setDialogOpen(false);
      navigate(`/decisions/${res.data.id}`);
    } catch {
      setError("Failed to create decision");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (decisionId: number) => {
    if (!window.confirm("Delete this decision?")) return;
    await decisionApi.delete(decisionId);
    load();
  };

  if (loading) return <Box display="flex" justifyContent="center" mt={4}><CircularProgress /></Box>;

  return (
    <Box>
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link component={RouterLink} to="/workspaces" underline="hover">Workspaces</Link>
        <Typography color="text.primary">{workspace?.name}</Typography>
      </Breadcrumbs>

      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold">{workspace?.name}</Typography>
          {workspace?.description && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {workspace.description}
            </Typography>
          )}
          {workspace?.goals && (
            <Typography variant="caption" color="text.secondary">
              🎯 Goals: {workspace.goals}
            </Typography>
          )}
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}>
          New Decision
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {decisions.length === 0 ? (
        <Card sx={{ p: 4, textAlign: "center" }}>
          <DecisionIcon sx={{ fontSize: 64, color: "text.secondary", mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>No decisions yet</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Create a decision to start evaluating trade-offs
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}>
            Create First Decision
          </Button>
        </Card>
      ) : (
        <Grid container spacing={2}>
          {decisions.map((d) => (
            <Grid item xs={12} md={6} key={d.id}>
              <Card sx={{ cursor: "pointer", "&:hover": { boxShadow: 4 }, transition: "box-shadow 0.2s" }}>
                <CardContent onClick={() => navigate(`/decisions/${d.id}`)}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      {d.title}
                    </Typography>
                    <Chip
                      label={d.status} size="small"
                      color={STATUS_COLORS[d.status] || "default"}
                    />
                  </Box>
                  {d.problem_statement && (
                    <Typography variant="body2" color="text.secondary">
                      {d.problem_statement.substring(0, 100)}
                      {d.problem_statement.length > 100 ? "..." : ""}
                    </Typography>
                  )}
                </CardContent>
                <CardActions sx={{ justifyContent: "space-between", px: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(d.updated_at).toLocaleDateString()}
                  </Typography>
                  <Box>
                    <Tooltip title="Delete">
                      <IconButton size="small" color="error" onClick={() => handleDelete(d.id)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Button size="small" onClick={() => navigate(`/decisions/${d.id}`)}>
                      Open →
                    </Button>
                  </Box>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Decision</DialogTitle>
        <Box component="form" onSubmit={handleSubmit(handleCreate)}>
          <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <TextField label="Title *" {...register("title", { required: true })} fullWidth autoFocus />
            <TextField label="Problem Statement" {...register("problem_statement")} fullWidth
              multiline rows={3} placeholder="What decision needs to be made?" />
            <TextField label="Success Metrics" {...register("success_metrics")} fullWidth
              multiline rows={2} placeholder="How will you measure success?" />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained" disabled={submitting}>
              {submitting ? <CircularProgress size={20} /> : "Create"}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Box>
  );
}
