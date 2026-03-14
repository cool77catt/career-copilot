"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { KeyboardEvent, useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tab,
  Tabs,
  TextField,
  Typography,
  alpha,
  useTheme,
} from "@mui/material";

import { ProfileResponse, autoLogin, fetchProfile, updateProfile } from "../lib/api";
import {
  JobProfileTarget,
  buildJobProfileId,
  formatTimestamp,
  readStoredJobProfiles,
  writeStoredJobProfiles,
} from "../lib/jobProfiles";
import { appPalette } from "../lib/theme/palette";

type AuthState = "loading" | "ready" | "error";

type Stage = {
  id: string;
  title: string;
  description: string;
  phase: string;
  focus: string;
  href?: string;
};

const stages: Stage[] = [
  {
    id: "user-profile",
    title: "User Profile",
    description: "Upload LinkedIn/resume PDFs, answer follow-up questions, and refine profile.md.",
    phase: "Phase 2",
    focus: "Parsing + profile memory",
  },
  {
    id: "linkedin-optimizer",
    title: "LinkedIn Optimizer",
    description: "Get role-targeted profile improvements for recruiter visibility.",
    phase: "Phase 3",
    focus: "Role-tuned profile guidance",
  },
  {
    id: "job-search",
    title: "Job Search",
    description: "Request 3 new opportunities from LinkedIn and Indeed.",
    phase: "Phase 4",
    focus: "Dedup + ranking",
  },
  {
    id: "job-selection",
    title: "Job Selection",
    description: "Accept, reject, or skip recommendations and keep status history.",
    phase: "Phase 5",
    focus: "Decision tracking",
  },
  {
    id: "materials",
    title: "Materials",
    description: "Generate versioned resume, cover-letter, and job-fit markdown files.",
    phase: "Phase 6",
    focus: "Versioned generation",
  },
];

const navItems: Stage[] = [
  {
    id: "overview",
    title: "Overview",
    description: "Dashboard metrics and trend cards.",
    phase: "Dashboard",
    focus: "KPI snapshot",
    href: "/",
  },
  {
    id: "profiles",
    title: "Profiles",
    description: "User Information and Job-Specific Profiles workspace.",
    phase: "Phase A",
    focus: "Profiles shell",
    href: "/profiles",
  },
  ...stages,
];

function renderMarkdownPreview(content: string) {
  const lines = content.split("\n");
  const nodes: React.ReactNode[] = [];
  let listBuffer: string[] = [];

  const flushList = () => {
    if (!listBuffer.length) return;
    nodes.push(
      <Box component="ul" sx={{ m: 0, pl: 2.4 }} key={`ul-${nodes.length}`}>
        {listBuffer.map((item, idx) => (
          <Typography key={`${item}-${idx}`} component="li" variant="body2" sx={{ mb: 0.45 }}>
            {item}
          </Typography>
        ))}
      </Box>,
    );
    listBuffer = [];
  };

  lines.forEach((line, idx) => {
    if (line.startsWith("- ")) {
      listBuffer.push(line.slice(2));
      return;
    }

    flushList();

    if (!line.trim()) {
      nodes.push(<Box key={`sp-${idx}`} sx={{ height: 8 }} />);
      return;
    }
    if (line.startsWith("### ")) {
      nodes.push(
        <Typography key={`h3-${idx}`} variant="subtitle1" sx={{ fontWeight: 700, mt: 1 }}>
          {line.slice(4)}
        </Typography>,
      );
      return;
    }
    if (line.startsWith("## ")) {
      nodes.push(
        <Typography key={`h2-${idx}`} variant="h6" sx={{ fontWeight: 700, mt: 1 }}>
          {line.slice(3)}
        </Typography>,
      );
      return;
    }
    if (line.startsWith("# ")) {
      nodes.push(
        <Typography key={`h1-${idx}`} variant="h5" sx={{ fontWeight: 700 }}>
          {line.slice(2)}
        </Typography>,
      );
      return;
    }

    nodes.push(
      <Typography key={`p-${idx}`} variant="body2">
        {line}
      </Typography>,
    );
  });

  flushList();
  return <Stack spacing={0.4}>{nodes}</Stack>;
}

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

type AppShellProps = {
  initialTab?: string;
};

export function AppShell({ initialTab = "overview" }: AppShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const isProfilesRoute = pathname === "/profiles" || pathname.startsWith("/profiles/");
  const routeProfileId = isProfilesRoute && pathname.startsWith("/profiles/") ? decodeURIComponent(pathname.split("/")[2] || "") : "";
  const [authState, setAuthState] = useState<AuthState>("loading");
  const [profileContent, setProfileContent] = useState("");
  const [profilePath, setProfilePath] = useState("");
  const [sectionMarkdownPaths, setSectionMarkdownPaths] = useState<Record<string, string>>({});
  const [profileReportLatestPath, setProfileReportLatestPath] = useState("");
  const [profileReportRevisionPaths, setProfileReportRevisionPaths] = useState<string[]>([]);
  const [followUpQuestions, setFollowUpQuestions] = useState<string[]>([]);
  const [followUpAnswers, setFollowUpAnswers] = useState<Record<string, string>>({});
  const [additionalInformation, setAdditionalInformation] = useState("");
  const [linkedinProfileFile, setLinkedinProfileFile] = useState<File | null>(null);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [hasLinkedinProfile, setHasLinkedinProfile] = useState(false);
  const [hasResume, setHasResume] = useState(false);
  const [profileLoading, setProfileLoading] = useState(false);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(initialTab);
  const [jobProfiles, setJobProfiles] = useState<JobProfileTarget[]>([]);
  const [profilesMenuOpen, setProfilesMenuOpen] = useState(isProfilesRoute);
  const [newJobProfileName, setNewJobProfileName] = useState("");
  const [jobProfilesReady, setJobProfilesReady] = useState(false);
  const [profileMarkdownView, setProfileMarkdownView] = useState<"raw" | "rendered">("rendered");
  const [profileMessage, setProfileMessage] = useState<{ severity: "success" | "info" | "error"; text: string } | null>(null);
  const theme = useTheme();

  const applyProfileState = (payload: ProfileResponse) => {
    setProfileContent(payload.content);
    setProfilePath(payload.profile_markdown_path);
    setSectionMarkdownPaths(payload.section_markdown_paths || {});
    setProfileReportLatestPath(payload.profile_report_latest_path || "");
    setProfileReportRevisionPaths(payload.profile_report_revision_paths || []);
    setFollowUpQuestions(payload.follow_up_questions);
    setFollowUpAnswers(payload.follow_up_answers || {});
    setAdditionalInformation(payload.additional_information || "");
    setHasLinkedinProfile(payload.has_linkedin_profile);
    setHasResume(payload.has_resume);
  };

  useEffect(() => {
    let active = true;
    autoLogin()
      .then(async (token) => {
        if (!active) return;
        window.localStorage.setItem("access_token", token);
        setAuthState("ready");

        setProfileLoading(true);
        try {
          const profile = await fetchProfile();
          if (!active) return;
          applyProfileState(profile);
          setProfileMessage({ severity: "info", text: "Profile workspace ready. Upload PDFs to build profile.md." });
        } catch (error) {
          if (!active) return;
          setProfileMessage({ severity: "error", text: error instanceof Error ? error.message : "Unable to load profile state." });
        } finally {
          if (active) setProfileLoading(false);
        }
      })
      .catch(() => {
        if (!active) return;
        setAuthState("error");
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    setActiveTab(initialTab);
  }, [initialTab]);

  useEffect(() => {
    if (isProfilesRoute) {
      setActiveTab("profiles");
      setProfilesMenuOpen(true);
    }
  }, [isProfilesRoute]);

  useEffect(() => {
    setJobProfiles(readStoredJobProfiles());
    setJobProfilesReady(true);
  }, []);

  useEffect(() => {
    if (!jobProfilesReady) return;
    writeStoredJobProfiles(jobProfiles);
  }, [jobProfiles, jobProfilesReady]);

  const handleFollowUpAnswerChange = (question: string, answer: string) => {
    setFollowUpAnswers((prev) => ({ ...prev, [question]: answer }));
  };

  const handleProfileUpdate = async () => {
    try {
      setUpdateLoading(true);
      const profile = await updateProfile({
        linkedinProfile: linkedinProfileFile,
        resume: resumeFile,
        followUpAnswers,
        additionalInformation,
      });
      applyProfileState(profile);
      setProfileMessage({
        severity: "success",
        text: "Profile updated. Profile report agent run has been queued.",
      });
      setLinkedinProfileFile(null);
      setResumeFile(null);
    } catch (error) {
      setProfileMessage({ severity: "error", text: error instanceof Error ? error.message : "Profile update failed." });
    } finally {
      setUpdateLoading(false);
    }
  };

  const handleAddJobProfile = () => {
    const name = newJobProfileName.trim();
    if (!name) return;
    if (jobProfiles.some((profile) => profile.name.toLowerCase() === name.toLowerCase())) {
      setProfileMessage({ severity: "error", text: "That job profile already exists." });
      return;
    }

    const id = buildJobProfileId(name, jobProfiles.map((profile) => profile.id));
    const now = new Date().toISOString();
    const nextProfiles = [{ id, name, updatedAt: now }, ...jobProfiles];
    setJobProfiles(nextProfiles);
    setNewJobProfileName("");
    setProfilesMenuOpen(true);
    setActiveTab("profiles");
    setProfileMessage({ severity: "success", text: `Added profile target: ${name}` });
    router.push(`/profiles/${id}`);
  };

  const handleOpenJobProfile = (profileId: string) => {
    setActiveTab("profiles");
    setProfilesMenuOpen(true);
    router.push(`/profiles/${encodeURIComponent(profileId)}`);
  };

  const selectedJobProfile = routeProfileId ? jobProfiles.find((profile) => profile.id === routeProfileId) : null;

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
            {navItems.map((item) => {
              const isProfilesItem = item.id === "profiles";
              const isActive = isProfilesItem ? activeTab === "profiles" || isProfilesRoute : activeTab === item.id;

              if (isProfilesItem) {
                return (
                  <Stack key={item.id} spacing={0.7}>
                    <Box
                      component={Link}
                      href="/profiles"
                      onClick={() => {
                        setActiveTab("profiles");
                        setProfilesMenuOpen((current) => !current);
                      }}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(event: KeyboardEvent<HTMLElement>) => {
                        if (event.key === "Enter" || event.key === " ") {
                          setActiveTab("profiles");
                          setProfilesMenuOpen((current) => !current);
                        }
                      }}
                      sx={{
                        p: 1.1,
                        borderRadius: 1,
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        cursor: "pointer",
                        background: isActive
                          ? `linear-gradient(135deg, ${appPalette.sidebar.nav.activeStart} 0%, ${appPalette.sidebar.nav.activeEnd} 100%)`
                          : alpha(appPalette.sidebar.nav.base, 0.02),
                        border: isActive
                          ? `1px solid ${appPalette.sidebar.nav.activeBorder}`
                          : `1px solid ${alpha(appPalette.sidebar.nav.border, 0.08)}`,
                        boxShadow: isActive ? `0 8px 20px ${appPalette.sidebar.nav.activeShadow}` : "none",
                        transition: "all 140ms ease",
                        textDecoration: "none",
                        "&:hover": {
                          background: isActive
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
                          color: isActive ? appPalette.sidebar.nav.iconTextActive : appPalette.sidebar.nav.iconText,
                          bgcolor: isActive
                            ? alpha(appPalette.sidebar.nav.iconBgActive, 0.72)
                            : alpha(appPalette.sidebar.nav.iconBg, 0.08),
                        }}
                      >
                        {item.title.slice(0, 1)}
                      </Box>
                      <Box sx={{ minWidth: 0, flexGrow: 1 }}>
                        <Typography
                          sx={{
                            fontWeight: isActive ? 700 : 500,
                            fontSize: 15,
                            color: isActive ? appPalette.sidebar.nav.labelActive : appPalette.sidebar.nav.label,
                            lineHeight: 1.25,
                            whiteSpace: "nowrap",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                          }}
                        >
                          {item.title}
                        </Typography>
                      </Box>
                      <Typography
                        sx={{
                          color: isActive ? appPalette.sidebar.nav.labelActive : appPalette.sidebar.nav.label,
                          fontSize: 14,
                          lineHeight: 1,
                        }}
                      >
                        {profilesMenuOpen ? "▾" : "▸"}
                      </Typography>
                    </Box>

                    {profilesMenuOpen && (
                      <Stack spacing={0.6} sx={{ pl: 1.3 }}>
                        <Box
                          component={Link}
                          href="/profiles"
                          onClick={() => setActiveTab("profiles")}
                          sx={{
                            borderRadius: 0.9,
                            px: 1.1,
                            py: 0.7,
                            textDecoration: "none",
                            border: `1px solid ${alpha(appPalette.sidebar.nav.border, 0.1)}`,
                            background: pathname === "/profiles" ? alpha(appPalette.sidebar.nav.activeStart, 0.22) : alpha(appPalette.sidebar.nav.base, 0.03),
                          }}
                        >
                          <Typography sx={{ fontSize: 13, fontWeight: 600, color: appPalette.sidebar.nav.label }}>Overview</Typography>
                        </Box>

                        {jobProfiles.map((profile) => (
                          <Box
                            key={profile.id}
                            component={Link}
                            href={`/profiles/${encodeURIComponent(profile.id)}`}
                            onClick={() => setActiveTab("profiles")}
                            sx={{
                              borderRadius: 0.9,
                              px: 1.1,
                              py: 0.7,
                              textDecoration: "none",
                              border: `1px solid ${alpha(appPalette.sidebar.nav.border, 0.1)}`,
                              background:
                                routeProfileId === profile.id ? alpha(appPalette.sidebar.nav.activeStart, 0.22) : alpha(appPalette.sidebar.nav.base, 0.03),
                            }}
                          >
                            <Typography
                              sx={{
                                fontSize: 13,
                                fontWeight: routeProfileId === profile.id ? 700 : 500,
                                color: appPalette.sidebar.nav.label,
                                whiteSpace: "nowrap",
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                              }}
                            >
                              {profile.name}
                            </Typography>
                          </Box>
                        ))}
                      </Stack>
                    )}
                  </Stack>
                );
              }

              return (
                <Box
                  key={item.id}
                  component={item.href ? Link : "div"}
                  href={item.href}
                  onClick={() => setActiveTab(item.id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(event: KeyboardEvent<HTMLElement>) => {
                    if (event.key === "Enter" || event.key === " ") {
                      setActiveTab(item.id);
                    }
                  }}
                  sx={{
                    p: 1.1,
                    borderRadius: 1,
                    display: "flex",
                    alignItems: "center",
                    gap: 1,
                    cursor: "pointer",
                    background: isActive
                      ? `linear-gradient(135deg, ${appPalette.sidebar.nav.activeStart} 0%, ${appPalette.sidebar.nav.activeEnd} 100%)`
                      : alpha(appPalette.sidebar.nav.base, 0.02),
                    border: isActive
                      ? `1px solid ${appPalette.sidebar.nav.activeBorder}`
                      : `1px solid ${alpha(appPalette.sidebar.nav.border, 0.08)}`,
                    boxShadow: isActive ? `0 8px 20px ${appPalette.sidebar.nav.activeShadow}` : "none",
                    transition: "all 140ms ease",
                    textDecoration: "none",
                    "&:hover": {
                      background: isActive
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
                      color: isActive ? appPalette.sidebar.nav.iconTextActive : appPalette.sidebar.nav.iconText,
                      bgcolor: isActive ? alpha(appPalette.sidebar.nav.iconBgActive, 0.72) : alpha(appPalette.sidebar.nav.iconBg, 0.08),
                    }}
                  >
                    {item.title.slice(0, 1)}
                  </Box>
                  <Box sx={{ minWidth: 0 }}>
                    <Typography
                      sx={{
                        fontWeight: isActive ? 700 : 500,
                        fontSize: 15,
                        color: isActive ? appPalette.sidebar.nav.labelActive : appPalette.sidebar.nav.label,
                        lineHeight: 1.25,
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                      }}
                    >
                      {item.title}
                    </Typography>
                  </Box>
                </Box>
              );
            })}
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

            {activeTab === "profiles" && !routeProfileId && (
              <Box
                sx={{
                  display: "grid",
                  gap: 2,
                  gridTemplateColumns: { xs: "1fr", xl: "repeat(2, minmax(0, 1fr))" },
                }}
              >
                <Paper elevation={0} sx={{ p: 2, borderRadius: 1.5, border: `1px solid ${theme.palette.divider}` }}>
                  <Stack spacing={1.2}>
                    <Typography variant="h6">User Information</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Global intake workspace for LinkedIn, resume(s), additional context, and generated user profile markdown.
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Phase B will attach full ingestion and profile generation controls here.
                    </Typography>
                  </Stack>
                </Paper>

                <Paper elevation={0} sx={{ p: 2, borderRadius: 1.5, border: `1px solid ${theme.palette.divider}` }}>
                  <Stack spacing={1.4}>
                    <Typography variant="h6">Job-Specific Profiles</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Overview includes all added job profile targets. Click any profile to open its route-backed workspace.
                    </Typography>

                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                      <TextField
                        fullWidth
                        size="small"
                        label="Add Job Profile"
                        placeholder="Senior Software Engineer"
                        value={newJobProfileName}
                        onChange={(event) => setNewJobProfileName(event.target.value)}
                        onKeyDown={(event) => {
                          if (event.key === "Enter") {
                            event.preventDefault();
                            handleAddJobProfile();
                          }
                        }}
                      />
                      <Button variant="contained" onClick={handleAddJobProfile} disabled={!newJobProfileName.trim()}>
                        Add
                      </Button>
                    </Stack>

                    <Box sx={{ border: `1px solid ${theme.palette.divider}`, borderRadius: 1, overflow: "hidden" }}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell sx={{ fontWeight: 700 }}>Profile</TableCell>
                            <TableCell sx={{ fontWeight: 700 }}>Last Updated</TableCell>
                            <TableCell align="right" sx={{ fontWeight: 700 }}>
                              Action
                            </TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {jobProfiles.length ? (
                            jobProfiles.map((profile) => (
                              <TableRow
                                key={profile.id}
                                hover
                                sx={{ cursor: "pointer" }}
                                onClick={() => handleOpenJobProfile(profile.id)}
                              >
                                <TableCell>{profile.name}</TableCell>
                                <TableCell>{formatTimestamp(profile.updatedAt)}</TableCell>
                                <TableCell align="right">
                                  <Button
                                    size="small"
                                    variant="outlined"
                                    onClick={(event) => {
                                      event.stopPropagation();
                                      handleOpenJobProfile(profile.id);
                                    }}
                                  >
                                    Open
                                  </Button>
                                </TableCell>
                              </TableRow>
                            ))
                          ) : (
                            <TableRow>
                              <TableCell colSpan={3}>
                                <Typography variant="body2" color="text.secondary">
                                  No job-specific profiles yet. Add one to create a route-backed workspace.
                                </Typography>
                              </TableCell>
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
                    </Box>
                  </Stack>
                </Paper>
              </Box>
            )}

            {activeTab === "profiles" && !!routeProfileId && (
              <Paper elevation={0} sx={{ p: 2, borderRadius: 1.5, border: `1px solid ${theme.palette.divider}` }}>
                <Stack spacing={1.5}>
                  <Stack direction={{ xs: "column", sm: "row" }} alignItems={{ xs: "flex-start", sm: "center" }} justifyContent="space-between">
                    <Box>
                      <Typography variant="h6">
                        {selectedJobProfile ? selectedJobProfile.name : "Job Profile Not Found"}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Route: `/profiles/{routeProfileId}`
                      </Typography>
                    </Box>
                    <Button variant="outlined" component={Link} href="/profiles" onClick={() => setActiveTab("profiles")}>
                      Back to Overview
                    </Button>
                  </Stack>

                  {!selectedJobProfile ? (
                    <Alert severity="warning">
                      This profile route does not match any saved job profile. Go back to Overview and add it there.
                    </Alert>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      This per-profile workspace is URL-backed and ready for Phase C/D artifact panels.
                    </Typography>
                  )}
                </Stack>
              </Paper>
            )}

            {activeTab === "user-profile" && (
            <Paper elevation={0} sx={{ p: 2, borderRadius: 1.5, border: `1px solid ${theme.palette.divider}` }}>
              <Stack spacing={1.6}>
                <Box>
                  <Typography variant="h6">Phase 2: Profile Builder</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Complete all profile sections, then click <b>Update Profile</b> once to persist your changes and
                    regenerate `profile.md`.
                  </Typography>
                </Box>

                <Paper elevation={0} sx={{ p: 1.5, border: `1px solid ${theme.palette.divider}`, borderRadius: 1 }}>
                  <Stack spacing={1}>
                    <Typography sx={{ fontWeight: 700 }}>1. LinkedIn Profile Input</Typography>
                    <Button component="label" variant="outlined">
                      Upload LinkedIn Profile (PDF)
                      <input
                        type="file"
                        hidden
                        accept=".pdf,application/pdf"
                        onChange={(event) => setLinkedinProfileFile(event.target.files?.[0] ?? null)}
                      />
                    </Button>
                    <Typography variant="caption" color="text.secondary">
                      {linkedinProfileFile
                        ? `Selected: ${linkedinProfileFile.name}`
                        : hasLinkedinProfile
                          ? "LinkedIn profile already on file"
                          : "No LinkedIn profile uploaded yet"}
                    </Typography>
                  </Stack>
                </Paper>

                <Paper elevation={0} sx={{ p: 1.5, border: `1px solid ${theme.palette.divider}`, borderRadius: 1 }}>
                  <Stack spacing={1}>
                    <Typography sx={{ fontWeight: 700 }}>2. Resume Input</Typography>
                    <Button component="label" variant="outlined">
                      Upload Resume (PDF)
                      <input
                        type="file"
                        hidden
                        accept=".pdf,application/pdf"
                        onChange={(event) => setResumeFile(event.target.files?.[0] ?? null)}
                      />
                    </Button>
                    <Typography variant="caption" color="text.secondary">
                      {resumeFile
                        ? `Selected: ${resumeFile.name}`
                        : hasResume
                          ? "Resume already on file"
                          : "No resume uploaded yet"}
                    </Typography>
                  </Stack>
                </Paper>

                <Paper elevation={0} sx={{ p: 1.5, border: `1px solid ${theme.palette.divider}`, borderRadius: 1 }}>
                  <Stack spacing={1}>
                    <Typography sx={{ fontWeight: 700 }}>3. Follow-up Questions and Answers</Typography>
                    {followUpQuestions.length ? (
                      followUpQuestions.map((question) => (
                        <TextField
                          key={question}
                          label={question}
                          value={followUpAnswers[question] || ""}
                          onChange={(event) => handleFollowUpAnswerChange(question, event.target.value)}
                          multiline
                          minRows={2}
                        />
                      ))
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No follow-up questions yet. Upload profile documents to generate questions.
                      </Typography>
                    )}
                  </Stack>
                </Paper>

                <Paper elevation={0} sx={{ p: 1.5, border: `1px solid ${theme.palette.divider}`, borderRadius: 1 }}>
                  <Stack spacing={1}>
                    <Typography sx={{ fontWeight: 700 }}>4. Additional Information</Typography>
                    <TextField
                      multiline
                      minRows={4}
                      value={additionalInformation}
                      onChange={(event) => setAdditionalInformation(event.target.value)}
                      placeholder="Add any other context that should improve profile quality and job matching."
                    />
                  </Stack>
                </Paper>

                <Stack direction="row" justifyContent="flex-end">
                  <Button variant="contained" disabled={updateLoading} onClick={handleProfileUpdate}>
                    {updateLoading ? "Updating..." : "Update Profile"}
                  </Button>
                </Stack>

                {profileMessage && <Alert severity={profileMessage.severity}>{profileMessage.text}</Alert>}

                <Paper elevation={0} sx={{ p: 1.5, border: `1px solid ${theme.palette.divider}`, borderRadius: 1 }}>
                  <Stack spacing={0.8}>
                    <Typography sx={{ fontWeight: 700 }}>Current profile.md</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {profilePath || "No profile path yet"}
                    </Typography>
                    <Stack spacing={0.35}>
                      {Object.entries(sectionMarkdownPaths).map(([key, value]) => (
                        <Typography key={key} variant="caption" color="text.secondary">
                          {key}: {value}
                        </Typography>
                      ))}
                    </Stack>
                    <Divider sx={{ my: 0.4 }} />
                    <Typography sx={{ fontWeight: 700 }}>Profile report history</Typography>
                    <Typography variant="caption" color="text.secondary">
                      latest: {profileReportLatestPath || "No profile report generated yet"}
                    </Typography>
                    <Stack spacing={0.35}>
                      {profileReportRevisionPaths.length ? (
                        profileReportRevisionPaths.map((path) => (
                          <Typography key={path} variant="caption" color="text.secondary">
                            revision: {path}
                          </Typography>
                        ))
                      ) : (
                        <Typography variant="caption" color="text.secondary">
                          No revisions yet
                        </Typography>
                      )}
                    </Stack>

                    <Tabs
                      value={profileMarkdownView}
                      onChange={(_, value) => setProfileMarkdownView(value)}
                      sx={{ minHeight: 36 }}
                    >
                      <Tab value="rendered" label="Rendered" sx={{ minHeight: 36 }} />
                      <Tab value="raw" label="Raw Markdown" sx={{ minHeight: 36 }} />
                    </Tabs>

                    <Box
                      sx={{
                        border: `1px solid ${theme.palette.divider}`,
                        background: alpha(theme.palette.primary.light, 0.04),
                        borderRadius: 1,
                        maxHeight: 320,
                        overflow: "auto",
                        p: 1.2,
                      }}
                    >
                      {profileLoading ? (
                        <Stack direction="row" spacing={1} alignItems="center">
                          <CircularProgress size={16} />
                          <Typography variant="body2">Loading profile content...</Typography>
                        </Stack>
                      ) : profileMarkdownView === "raw" ? (
                        <Typography
                          component="pre"
                          sx={{ m: 0, fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", fontSize: 12, whiteSpace: "pre-wrap" }}
                        >
                          {profileContent || "Profile markdown will appear here after update."}
                        </Typography>
                      ) : (
                        renderMarkdownPreview(profileContent || "No profile markdown generated yet.")
                      )}
                    </Box>
                  </Stack>
                </Paper>
              </Stack>
            </Paper>
            )}

            {activeTab === "overview" && (
              <>
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
              </>
            )}

            {activeTab !== "overview" && activeTab !== "user-profile" && activeTab !== "profiles" && (
              <Paper elevation={0} sx={{ p: 2, borderRadius: 1.5, border: `1px solid ${theme.palette.divider}` }}>
                <Stack spacing={1}>
                  <Typography variant="h6">
                    {navItems.find((item) => item.id === activeTab)?.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {navItems.find((item) => item.id === activeTab)?.description}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    This phase is queued in the roadmap. We can implement this tab next.
                  </Typography>
                </Stack>
              </Paper>
            )}
          </Stack>
        </Box>
      </Box>
    </Box>
  );
}
