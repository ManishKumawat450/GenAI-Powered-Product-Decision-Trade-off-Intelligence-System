import React, { useEffect, useState } from "react";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import {
  Box, Typography, Button, Card, CardContent, CardActions, Grid, Dialog,
  DialogTitle, DialogContent, DialogActions, TextField, CircularProgress,
  Alert, Chip, IconButton, Tooltip,
} from "@mui/material";
import {
  Add as AddIcon, Folder as FolderIcon, Delete as DeleteIcon, Edit as EditIcon,
} from "@mui/icons-material";
import { useForm } from "react-hook-form";
import { workspaceApi } from "../api/endpoints";
import { Workspace } from "../api/types";

interface WsForm {
  name: string; description?: string; goals?: string; context?: string;
}

export function WorkspacesPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const { register, handleSubmit, reset } = useForm<WsForm>();

  const load = async () => {
    try {
      setLoading(true);
      const res = await workspaceApi.list();
      setWorkspaces(res.data);
    } catch {
      setError("Failed to load workspaces");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (data: WsForm) => {
    setSubmitting(true);
    try {
      await workspaceApi.create(data);
      reset();
      setDialogOpen(false);
      load();
    } catch {
      setError("Failed to create workspace");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Delete this workspace and all its decisions?")) return;
    await workspaceApi.delete(id);
    load();
  };

  if (loading) return <Box display="flex" justifyContent="center" mt={4}><CircularProgress /></Box>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold">Workspaces</Typography>
          <Typography variant="body2" color="text.secondary">
            Organize your product decisions into workspaces
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}>
          New Workspace
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {workspaces.length === 0 ? (
        <Card sx={{ p: 4, textAlign: "center" }}>
          <FolderIcon sx={{ fontSize: 64, color: "text.secondary", mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>No workspaces yet</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Create a workspace to start organizing your product decisions
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}>
            Create First Workspace
          </Button>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {workspaces.map((ws) => (
            <Grid item xs={12} sm={6} md={4} key={ws.id}>
              <Card sx={{ height: "100%", display: "flex", flexDirection: "column", cursor: "pointer",
                "&:hover": { boxShadow: 4 }, transition: "box-shadow 0.2s" }}>
                <CardContent sx={{ flex: 1 }} onClick={() => navigate(`/workspaces/${ws.id}`)}>
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    <FolderIcon color="primary" />
                    <Typography variant="h6" fontWeight="bold" noWrap>{ws.name}</Typography>
                  </Box>
                  {ws.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {ws.description}
                    </Typography>
                  )}
                  {ws.goals && (
                    <Typography variant="caption" color="text.secondary">
                      🎯 {ws.goals.substring(0, 80)}{ws.goals.length > 80 ? "..." : ""}
                    </Typography>
                  )}
                </CardContent>
                <CardActions sx={{ justifyContent: "space-between", px: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(ws.created_at).toLocaleDateString()}
                  </Typography>
                  <Box>
                    <Tooltip title="Delete workspace">
                      <IconButton size="small" color="error" onClick={() => handleDelete(ws.id)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Button size="small" onClick={() => navigate(`/workspaces/${ws.id}`)}>
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
        <DialogTitle>Create New Workspace</DialogTitle>
        <Box component="form" onSubmit={handleSubmit(handleCreate)}>
          <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <TextField label="Name *" {...register("name", { required: true })} fullWidth autoFocus />
            <TextField label="Description" {...register("description")} fullWidth multiline rows={2} />
            <TextField label="Goals" {...register("goals")} fullWidth multiline rows={2}
              placeholder="What are the main objectives for this workspace?" />
            <TextField label="Context" {...register("context")} fullWidth multiline rows={2}
              placeholder="Background context (company stage, team size, etc.)" />
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
