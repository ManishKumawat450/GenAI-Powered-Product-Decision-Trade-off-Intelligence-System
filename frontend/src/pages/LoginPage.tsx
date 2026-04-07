import React, { useState } from "react";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import { useForm } from "react-hook-form";
import {
  Box, Paper, Typography, TextField, Button, Alert, Tabs, Tab, CircularProgress, Divider,
} from "@mui/material";
import { Psychology as BrainIcon } from "@mui/icons-material";
import { authApi } from "../api/endpoints";
import { useAuth } from "../contexts/AuthContext";

interface LoginForm { email: string; password: string }
interface RegisterForm { email: string; username: string; password: string; role: string }

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const loginForm = useForm<LoginForm>();
  const registerForm = useForm<RegisterForm>({ defaultValues: { role: "viewer" } });

  const handleLogin = async (data: LoginForm) => {
    setError("");
    setLoading(true);
    try {
      const res = await authApi.login(data);
      await login(res.data.access_token);
      navigate("/workspaces");
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (data: RegisterForm) => {
    setError("");
    setLoading(true);
    try {
      await authApi.register(data);
      const res = await authApi.login({ email: data.email, password: data.password });
      await login(res.data.access_token);
      navigate("/workspaces");
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
        bgcolor: "grey.100",
      }}
    >
      <Paper elevation={3} sx={{ p: 4, width: 400, maxWidth: "95%" }}>
        <Box sx={{ display: "flex", alignItems: "center", mb: 2, gap: 1 }}>
          <BrainIcon color="primary" sx={{ fontSize: 36 }} />
          <Box>
            <Typography variant="h6" fontWeight="bold">Decision Intelligence</Typography>
            <Typography variant="caption" color="text.secondary">
              Product Trade-off Analysis Platform
            </Typography>
          </Box>
        </Box>
        <Divider sx={{ mb: 2 }} />

        <Tabs value={tab} onChange={(_, v) => { setTab(v); setError(""); }} sx={{ mb: 2 }}>
          <Tab label="Sign In" />
          <Tab label="Register" />
        </Tabs>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {tab === 0 ? (
          <Box component="form" onSubmit={loginForm.handleSubmit(handleLogin)} sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <TextField label="Email" type="email" {...loginForm.register("email", { required: true })} fullWidth />
            <TextField label="Password" type="password" {...loginForm.register("password", { required: true })} fullWidth />
            <Button type="submit" variant="contained" size="large" disabled={loading}>
              {loading ? <CircularProgress size={24} /> : "Sign In"}
            </Button>
            <Typography variant="body2" color="text.secondary" align="center">
              Demo: admin@example.com / Admin123!
            </Typography>
          </Box>
        ) : (
          <Box component="form" onSubmit={registerForm.handleSubmit(handleRegister)} sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <TextField label="Email" type="email" {...registerForm.register("email", { required: true })} fullWidth />
            <TextField label="Username" {...registerForm.register("username", { required: true })} fullWidth />
            <TextField label="Password" type="password" {...registerForm.register("password", { required: true })} fullWidth />
            <TextField
              label="Role" select SelectProps={{ native: true }}
              {...registerForm.register("role")} fullWidth
            >
              <option value="viewer">Viewer</option>
              <option value="pm">PM</option>
              <option value="admin">Admin</option>
            </TextField>
            <Button type="submit" variant="contained" size="large" disabled={loading}>
              {loading ? <CircularProgress size={24} /> : "Create Account"}
            </Button>
          </Box>
        )}
      </Paper>
    </Box>
  );
}
