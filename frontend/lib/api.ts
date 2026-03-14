const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const DEV_EMAIL = process.env.NEXT_PUBLIC_DEV_EMAIL || "chris77carl@gmail.com";
const DEV_PASSWORD = process.env.NEXT_PUBLIC_DEV_PASSWORD || "default";

export type ProfileResponse = {
  profile_markdown_path: string;
  section_markdown_paths: Record<string, string>;
  profile_report_latest_path?: string | null;
  profile_report_revision_paths?: string[];
  content: string;
  follow_up_questions: string[];
  follow_up_answers: Record<string, string>;
  additional_information: string;
  has_linkedin_profile: boolean;
  has_resume: boolean;
  updated_at: string | null;
};

export async function autoLogin(): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email: DEV_EMAIL, password: DEV_PASSWORD }),
  });

  if (!response.ok) {
    throw new Error("Auto-login failed");
  }

  const body = await response.json();
  return body.access_token;
}

function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("access_token");
}

function getAuthHeaders(): Record<string, string> {
  const token = getAccessToken();
  if (!token) {
    throw new Error("Missing access token");
  }
  return { Authorization: `Bearer ${token}` };
}

async function parseApiError(response: Response): Promise<never> {
  let detail = "Request failed";
  try {
    const body = await response.json();
    detail = body.detail || detail;
  } catch {
    // keep fallback detail
  }
  throw new Error(detail);
}

export async function fetchProfile(): Promise<ProfileResponse> {
  const response = await fetch(`${API_BASE_URL}/profile`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    await parseApiError(response);
  }

  return response.json();
}

export type UpdateProfilePayload = {
  linkedinProfile: File | null;
  resume: File | null;
  followUpAnswers: Record<string, string>;
  additionalInformation: string;
};

export async function updateProfile(payload: UpdateProfilePayload): Promise<ProfileResponse> {
  const formData = new FormData();
  if (payload.linkedinProfile) {
    formData.append("linkedin_profile", payload.linkedinProfile);
  }
  if (payload.resume) {
    formData.append("resume", payload.resume);
  }
  formData.append("follow_up_answers", JSON.stringify(payload.followUpAnswers));
  formData.append("additional_information", payload.additionalInformation);

  const response = await fetch(`${API_BASE_URL}/profile/update`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!response.ok) {
    await parseApiError(response);
  }

  return response.json();
}
