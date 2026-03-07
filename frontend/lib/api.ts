const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const DEV_EMAIL = process.env.NEXT_PUBLIC_DEV_EMAIL || "chris77carl@gmail.com";
const DEV_PASSWORD = process.env.NEXT_PUBLIC_DEV_PASSWORD || "default";

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
