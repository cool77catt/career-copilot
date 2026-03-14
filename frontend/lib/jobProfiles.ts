export type JobProfileTarget = {
  id: string;
  name: string;
  updatedAt: string;
};

const JOB_PROFILE_STORAGE_KEY = "career_copilot_job_profiles";

function normalizeWhitespace(value: string): string {
  return value.trim().replace(/\s+/g, " ");
}

function slugify(value: string): string {
  return normalizeWhitespace(value)
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

export function buildJobProfileId(name: string, existingIds: string[]): string {
  const base = slugify(name) || "profile";
  let candidate = base;
  let index = 2;
  while (existingIds.includes(candidate)) {
    candidate = `${base}-${index}`;
    index += 1;
  }
  return candidate;
}

export function readStoredJobProfiles(): JobProfileTarget[] {
  if (typeof window === "undefined") return [];
  const raw = window.localStorage.getItem(JOB_PROFILE_STORAGE_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((item) => item && typeof item.id === "string" && typeof item.name === "string")
      .map((item) => ({
        id: item.id,
        name: item.name,
        updatedAt: typeof item.updatedAt === "string" ? item.updatedAt : new Date().toISOString(),
      }));
  } catch {
    return [];
  }
}

export function writeStoredJobProfiles(profiles: JobProfileTarget[]): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(JOB_PROFILE_STORAGE_KEY, JSON.stringify(profiles));
}

export function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown";
  return date.toLocaleString();
}
