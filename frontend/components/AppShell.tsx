"use client";

import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Chip,
  Divider,
  Paper,
  Stack,
  Typography,
  alpha,
  useTheme,
} from "@mui/material";

import { autoLogin } from "../lib/api";
import { appPalette } from "../lib/theme/palette";

type AuthState = "loading" | "ready" | "error";

type Stage = {
  title: string;
  description: string;
  phase: string;
  focus: string;
};

const stages: Stage[] = [
  {
    title: "User Profile",
    description: "Upload LinkedIn/resume PDFs, answer follow-up questions, and refine profile.md.",
    phase: "Phase 2",
    focus: "Parsing + profile memory",
  },
  {
    title: "LinkedIn Optimizer",
    description: "Get role-targeted profile improvements for recruiter visibility.",
    phase: "Phase 3",
    focus: "Role-tuned profile guidance",
  },
  {
    title: "Job Search",
    description: "Request 3 new opportunities from LinkedIn and Indeed.",
    phase: "Phase 4",
    focus: "Dedup + ranking",
  },
  {
    title: "Job Selection",
    description: "Accept, reject, or skip recommendations and keep status history.",
    phase: "Phase 5",
    focus: "Decision tracking",
  },
  {
    title: "Materials",
    description: "Generate versioned resume, cover-letter, and job-fit markdown files.",
    phase: "Phase 6",
    focus: "Versioned generation",
  },
];

function AuthBanner({ authState }: { authState: AuthState }) {
  if (authState === "loading") {
    return (
      <Alert
        severity="info"
        sx={{
          border: `1px solid ${appPalette.status.info.border}`,
          bgcolor: appPalette.status.info.bg,
          color: appPalette.status.info.text,
        }}
      >
        Authenticating with backend...
      </Alert>
    );
  }

  if (authState === "ready") {
    return (
      <Alert
        severity="info"
        sx={{
          border: `1px solid ${appPalette.status.info.border}`,
          bgcolor: appPalette.status.info.bg,
          color: appPalette.status.info.text,
        }}
      >
        Authenticated as seeded user.
      </Alert>
    );
  }

  return (
    <Alert
      severity="error"
      sx={{
        border: `1px solid ${appPalette.status.error.border}`,
        bgcolor: appPalette.status.error.bg,
        color: appPalette.status.error.text,
        "& .MuiAlert-icon": { color: appPalette.status.error.icon },
      }}
    >
      Auto-login failed. Check backend or env values.
    </Alert>
  );
}

export function AppShell() {
  const [authState, setAuthState] = useState<AuthState>("loading");
  const theme = useTheme();

  useEffect(() => {
    let active = true;
    autoLogin()
      .then((token) => {
        if (!active) return;
        window.localStorage.setItem("access_token", token);
        setAuthState("ready");
      })
      .catch(() => {
        if (!active) return;
        setAuthState("error");
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: appPalette.core.canvas,
      }}
    >
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", md: "280px minmax(0, 1fr)" },
          minHeight: "100vh",
        }}
      >
        <Box
          component="aside"
          sx={{
            p: 2,
            color: appPalette.sidebar.text,
            background: appPalette.sidebar.backgroundGradient,
            borderRight: `1px solid ${alpha(appPalette.sidebar.border, 0.24)}`,
          }}
        >
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.1 }}>
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                bgcolor: appPalette.sidebar.dot,
                boxShadow: `0 0 12px ${appPalette.sidebar.dotGlow}`,
              }}
            />
            <Typography sx={{ letterSpacing: 0.4, fontSize: 16, fontWeight: 700, color: appPalette.sidebar.titleText }}>
              Career Copilot
            </Typography>
          </Stack>
          <Divider sx={{ borderColor: alpha(appPalette.sidebar.divider, 0.2), mb: 1.6 }} />

          <Stack spacing={1}>
            {stages.map((stage, idx) => (
              <Box
                key={stage.title}
                sx={{
                  p: 1.1,
                  borderRadius: 1,
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                  background:
                    idx === 0
                      ? `linear-gradient(135deg, ${appPalette.sidebar.nav.activeStart} 0%, ${appPalette.sidebar.nav.activeEnd} 100%)`
                      : alpha(appPalette.sidebar.nav.base, 0.02),
                  border:
                    idx === 0
                      ? `1px solid ${appPalette.sidebar.nav.activeBorder}`
                      : `1px solid ${alpha(appPalette.sidebar.nav.border, 0.08)}`,
                  boxShadow: idx === 0 ? `0 8px 20px ${appPalette.sidebar.nav.activeShadow}` : "none",
                  transition: "all 140ms ease",
                  "&:hover": {
                    background:
                      idx === 0
                        ? `linear-gradient(135deg, ${appPalette.sidebar.nav.activeStart} 0%, ${appPalette.sidebar.nav.activeEnd} 100%)`
                        : alpha(appPalette.sidebar.nav.base, 0.06),
                  },
                }}
              >
                <Box
                  sx={{
                    width: 22,
                    height: 22,
                    borderRadius: 0.75,
                    display: "grid",
                    placeItems: "center",
                    fontSize: 11,
                    fontWeight: 700,
                    color: idx === 0 ? appPalette.sidebar.nav.iconTextActive : appPalette.sidebar.nav.iconText,
                    bgcolor:
                      idx === 0 ? alpha(appPalette.sidebar.nav.iconBgActive, 0.72) : alpha(appPalette.sidebar.nav.iconBg, 0.08),
                  }}
                >
                  {stage.title.slice(0, 1)}
                </Box>
                <Box sx={{ minWidth: 0 }}>
                  <Typography
                    sx={{
                      fontWeight: idx === 0 ? 700 : 500,
                      fontSize: 15,
                      color: idx === 0 ? appPalette.sidebar.nav.labelActive : appPalette.sidebar.nav.label,
                      lineHeight: 1.25,
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {stage.title}
                  </Typography>
                </Box>
              </Box>
            ))}
          </Stack>
        </Box>

        <Box component="main" sx={{ p: { xs: 2, md: 3 } }}>
          <Stack spacing={2}>
            <Stack
              direction={{ xs: "column", sm: "row" }}
              justifyContent="space-between"
              alignItems={{ xs: "flex-start", sm: "center" }}
              spacing={1}
            >
              <Box>
                <Typography variant="h4" sx={{ color: appPalette.core.title }}>
                  Career Copilot
                </Typography>
                <Typography color="text.secondary" sx={{ mt: 0.3 }}>
                  Startup-modern command center for job search automation
                </Typography>
              </Box>
              <Stack direction="row" spacing={1}>
                <Chip label="Dashboard" color="primary" />
                <Chip label="Live Shell" variant="outlined" />
              </Stack>
            </Stack>

            <AuthBanner authState={authState} />

            <Box
              sx={{
                display: "grid",
                gap: 2,
                gridTemplateColumns: { xs: "1fr", sm: "repeat(2, minmax(0, 1fr))", xl: "repeat(4, minmax(0, 1fr))" },
              }}
            >
              {[
                { label: "Profile Completeness", value: "84%", color: appPalette.metrics.profileCompleteness },
                { label: "Weekly Job Matches", value: "18", color: appPalette.metrics.weeklyMatches },
                { label: "Open Decisions", value: "5", color: appPalette.metrics.openDecisions },
                { label: "Generated Assets", value: "24", color: appPalette.metrics.generatedAssets },
              ].map((metric) => (
                <Paper
                  key={metric.label}
                  elevation={0}
                  sx={{ p: 1.6, borderRadius: 1.5, border: `1px solid ${theme.palette.divider}`, background: appPalette.core.surface }}
                >
                  <Stack direction="row" spacing={1.3} alignItems="center">
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 1,
                        bgcolor: metric.color,
                        boxShadow: `0 10px 20px ${alpha(metric.color, 0.35)}`,
                      }}
                    />
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {metric.label}
                      </Typography>
                      <Typography sx={{ fontWeight: 800, fontSize: 28, lineHeight: 1.1 }}>{metric.value}</Typography>
                    </Box>
                  </Stack>
                </Paper>
              ))}
            </Box>

            <Box
              sx={{
                display: "grid",
                gap: 2,
                gridTemplateColumns: { xs: "1fr", lg: "repeat(3, minmax(0, 1fr))" },
              }}
            >
              {[
                { title: "Profile Growth", color: appPalette.panels.profileGrowth, note: "55% increase in role-fit signal depth." },
                { title: "Match Velocity", color: appPalette.panels.matchVelocity, note: "Average 3 new recommendations per run." },
                {
                  title: "Application Readiness",
                  color: appPalette.panels.applicationReadiness,
                  note: "Asset regeneration latency trending down.",
                },
              ].map((panel) => (
                <Paper
                  key={panel.title}
                  elevation={0}
                  sx={{ p: 1.8, borderRadius: 1.5, border: `1px solid ${theme.palette.divider}`, background: appPalette.core.surface }}
                >
                  <Box
                    sx={{
                      borderRadius: 1.5,
                      height: 170,
                      background: `linear-gradient(135deg, ${panel.color} 0%, ${alpha(panel.color, 0.75)} 100%)`,
                      boxShadow: `0 12px 22px ${alpha(panel.color, 0.35)}`,
                    }}
                  />
                  <Typography sx={{ mt: 1.5, fontWeight: 700 }}>{panel.title}</Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.4 }}>
                    {panel.note}
                  </Typography>
                  <Divider sx={{ my: 1.3 }} />
                  <Typography variant="caption" color="text.secondary">
                    Updated moments ago
                  </Typography>
                </Paper>
              ))}
            </Box>
          </Stack>
        </Box>
      </Box>
    </Box>
  );
}
