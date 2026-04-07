import React, { useEffect, useState } from "react";
import {
  Box, Typography, Card, CardContent, Chip, Grid, Alert, CircularProgress,
  Paper, Table, TableBody, TableCell, TableHead, TableRow, Divider,
} from "@mui/material";
import { criteriaApi } from "../api/endpoints";
import { Criterion } from "../api/types";
import { useAuth } from "../contexts/AuthContext";

const TEMPLATE_WEIGHTS: Record<string, Record<string, number>> = {
  "MVP Features": {
    "User Value": 0.30, "Engineering Effort": 0.25, "Time-to-Market": 0.20,
    "Risk": 0.10, "Cost": 0.10, "Maintainability": 0.03, "Strategic Alignment": 0.01, "Compliance/Privacy": 0.01,
  },
  "Platform Investment": {
    "User Value": 0.10, "Engineering Effort": 0.15, "Time-to-Market": 0.05,
    "Risk": 0.10, "Cost": 0.15, "Maintainability": 0.20, "Strategic Alignment": 0.20, "Compliance/Privacy": 0.05,
  },
  "Regulated Product": {
    "User Value": 0.15, "Engineering Effort": 0.10, "Time-to-Market": 0.10,
    "Risk": 0.20, "Cost": 0.10, "Maintainability": 0.10, "Strategic Alignment": 0.05, "Compliance/Privacy": 0.20,
  },
  "Cost Optimization": {
    "User Value": 0.10, "Engineering Effort": 0.15, "Time-to-Market": 0.10,
    "Risk": 0.10, "Cost": 0.35, "Maintainability": 0.10, "Strategic Alignment": 0.05, "Compliance/Privacy": 0.05,
  },
};

export function SettingsPage() {
  const { user } = useAuth();
  const [criteria, setCriteria] = useState<Criterion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    criteriaApi.list()
      .then((res) => setCriteria(res.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress />;

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>Settings</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        System configuration, criteria definitions, and weight templates
      </Typography>

      <Grid container spacing={3}>
        {/* User info */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>Account</Typography>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="body2"><b>Email:</b> {user?.email}</Typography>
              <Typography variant="body2"><b>Username:</b> {user?.username}</Typography>
              <Box sx={{ mt: 1 }}>
                <b>Roles:</b>{" "}
                {user?.roles.map((r) => <Chip key={r} label={r} size="small" sx={{ mr: 0.5 }} />)}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* LLM config */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>LLM Integration</Typography>
              <Divider sx={{ mb: 2 }} />
              <Alert severity="info" sx={{ mb: 1 }}>
                Currently running in <b>deterministic mode</b> (no LLM API key configured).
              </Alert>
              <Typography variant="body2" color="text.secondary">
                Set <code>LLM_PROVIDER</code> and <code>LLM_API_KEY</code> in backend <code>.env</code> to
                enable LLM-enhanced narrative generation. Numeric scores are never modified by LLM.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk thresholds */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>Score Thresholds</Typography>
              <Divider sx={{ mb: 2 }} />
              <Table size="small">
                <TableBody>
                  <TableRow><TableCell>✅ Strong</TableCell><TableCell>≥ 70/100</TableCell></TableRow>
                  <TableRow><TableCell>⚠️ Viable</TableCell><TableCell>50–69/100</TableCell></TableRow>
                  <TableRow><TableCell>❌ Weak</TableCell><TableCell>&lt; 50/100</TableCell></TableRow>
                  <TableRow><TableCell>🔴 Risk flag</TableCell><TableCell>Criterion score ≤ 3/10</TableCell></TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Grid>

        {/* Criteria */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Global Criteria Definitions ({criteria.length})
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                {criteria.map((c) => (
                  <Grid item xs={12} sm={6} md={3} key={c.id}>
                    <Paper variant="outlined" sx={{ p: 1.5 }}>
                      <Typography fontWeight="bold" variant="body2">{c.name}</Typography>
                      <Typography variant="caption" color="text.secondary">{c.description}</Typography>
                      <br />
                      <Chip label={c.is_global ? "Global" : "Custom"} size="small" sx={{ mt: 0.5 }} />
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Weight templates */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>Criteria Weight Templates</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Apply these templates to your decisions from the Decision Detail page → Criteria Weights tab.
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(TEMPLATE_WEIGHTS).map(([templateName, weights]) => (
                  <Grid item xs={12} md={6} key={templateName}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography fontWeight="bold" gutterBottom>{templateName}</Typography>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Criterion</TableCell>
                            <TableCell align="right">Weight</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {Object.entries(weights).map(([name, w]) => (
                            <TableRow key={name}>
                              <TableCell>{name}</TableCell>
                              <TableCell align="right">{(w * 100).toFixed(0)}%</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
