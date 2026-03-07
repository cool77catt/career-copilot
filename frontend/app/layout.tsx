import type { Metadata } from "next";
import "./globals.css";
import { AppThemeProvider } from "../components/AppThemeProvider";

export const metadata: Metadata = {
  title: "Career Copilot",
  description: "Job hunting workflow assistant",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppThemeProvider>{children}</AppThemeProvider>
      </body>
    </html>
  );
}
