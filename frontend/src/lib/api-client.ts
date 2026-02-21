import { getSession } from "next-auth/react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getAuthHeaders(): Promise<HeadersInit> {
  const session = await getSession();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (session?.accessToken) {
    headers["Authorization"] = `Bearer ${session.accessToken}`;
  }

  return headers;
}

async function getAuthToken(): Promise<string | null> {
  const session = await getSession();
  return (session?.accessToken as string) || null;
}

export const apiClient = {
  async get<T>(path: string): Promise<T> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}${path}`, { headers });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `API error: ${res.status}`);
    }
    return res.json();
  },

  async post<T>(path: string, body?: unknown): Promise<T> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `API error: ${res.status}`);
    }
    return res.json();
  },

  async delete(path: string): Promise<void> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${API_BASE}${path}`, {
      method: "DELETE",
      headers,
    });
    if (!res.ok && res.status !== 204) {
      const error = await res.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `API error: ${res.status}`);
    }
  },

  async upload<T>(path: string, formData: FormData): Promise<T> {
    const token = await getAuthToken();
    const headers: HeadersInit = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers,
      body: formData,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `API error: ${res.status}`);
    }
    return res.json();
  },

  getApiBase() {
    return API_BASE;
  },

  getAuthToken,
};
