const defaultApiUrl = "https://velvorax-careers.onrender.com/api/v1";
const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL;
const configuredApiIsLocal =
  configuredApiUrl &&
  /^https?:\/\/(localhost|127\.0\.0\.1|\[::1\])(:\d+)?(?:\/|$)/i.test(configuredApiUrl);
const runningOnLocalhost =
  typeof window !== "undefined" &&
  /^(localhost|127\.0\.0\.1|\[::1\])$/i.test(window.location.hostname);
const useConfiguredApiUrl = configuredApiUrl && (!configuredApiIsLocal || runningOnLocalhost);

export const API_BASE_URL = (
  (useConfiguredApiUrl && configuredApiUrl) || defaultApiUrl
).replace(/\/+$/, "");

export function formatISTDate(value: string | Date, includeTime = false): string {
  return new Intl.DateTimeFormat("en-IN", {
    timeZone: "Asia/Kolkata",
    dateStyle: "medium",
    ...(includeTime ? { timeStyle: "short" as const } : {}),
  }).format(new Date(value));
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  phone?: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
}

export interface AuthState {
  token: string | null;
  user: User | null;
  role: string | null;
}

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("velvorax_auth_token");
}

export function getAuthUser(): User | null {
  if (typeof window === "undefined") return null;
  const userStr = localStorage.getItem("velvorax_auth_user");
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

export function saveAuth(token: string, user: User) {
  if (typeof window === "undefined") return;
  localStorage.setItem("velvorax_auth_token", token);
  localStorage.setItem("velvorax_auth_user", JSON.stringify(user));
  localStorage.setItem("velvorax_auth_role", user.role);
}

export function clearAuth() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("velvorax_auth_token");
  localStorage.removeItem("velvorax_auth_user");
  localStorage.removeItem("velvorax_auth_role");
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = endpoint.startsWith("http")
    ? endpoint
    : `${API_BASE_URL}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = "An unexpected error occurred.";
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch {
      errorDetail = await response.text();
    }
    throw new Error(errorDetail || `HTTP Error ${response.status}`);
  }

  return response.json();
}
