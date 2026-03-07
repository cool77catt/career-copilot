"use client";

import { CssBaseline, GlobalStyles, ThemeProvider, createTheme, alpha } from "@mui/material";
import { appPalette } from "../lib/theme/palette";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: appPalette.mui.primary,
      dark: appPalette.mui.primaryDark,
    },
    secondary: {
      main: appPalette.mui.secondary,
    },
    background: {
      default: appPalette.mui.backgroundDefault,
      paper: appPalette.mui.backgroundPaper,
    },
    text: {
      primary: appPalette.mui.textPrimary,
      secondary: appPalette.mui.textSecondary,
    },
  },
  shape: {
    borderRadius: 4,
  },
  typography: {
    fontFamily: '"DM Sans", "Manrope", "Avenir Next", "Segoe UI", sans-serif',
    h3: {
      fontFamily: '"IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif',
      fontWeight: 700,
      letterSpacing: -0.25,
      lineHeight: 1.12,
    },
    h4: {
      fontFamily: '"IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif',
      fontWeight: 700,
      letterSpacing: -0.25,
      lineHeight: 1.14,
    },
    h5: {
      fontWeight: 700,
      letterSpacing: -0.2,
    },
    h6: {
      fontWeight: 700,
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: `0 14px 34px ${alpha(appPalette.core.shadowBase, 0.08)}`,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 600,
          borderRadius: 5,
          height: 36,
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 4,
        },
      },
    },
  },
});

export function AppThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <GlobalStyles
        styles={{
          ":root": {
            "--cc-canvas": appPalette.core.canvas,
            "--cc-surface": appPalette.core.surface,
            "--cc-title": appPalette.core.title,
            "--cc-accent-primary": appPalette.mui.primary,
            "--cc-accent-secondary": appPalette.mui.secondary,
            "--cc-accent-magenta": appPalette.metrics.openDecisions,
          },
          body: {
            margin: 0,
          },
        }}
      />
      {children}
    </ThemeProvider>
  );
}
