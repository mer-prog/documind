const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Client-side token cache to avoid redundant /api/auth/token calls
let _cachedToken: string | null = null;
let _tokenExpiry = 0;

async function fetchBackendToken(): Promise<string | null> {
  // Return cached token if still valid (50-min cache for 1-hour token)
  if (_cachedToken && Date.now() < _tokenExpiry) {
    return _cachedToken;
  }
  try {
    const res = await fetch("/api/auth/token");
    if (!res.ok) {
      _cachedToken = null;
      return null;
    }
    const data = await res.json();
    _cachedToken = data.token || null;
    if (_cachedToken) {
      _tokenExpiry = Date.now() + 50 * 60 * 1000; // 50 minutes
    }
    return _cachedToken;
  } catch {
    _cachedToken = null;
    return null;
  }
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const token = await fetchBackendToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

async function getAuthToken(): Promise<string | null> {
  return fetchBackendToken();
}

export function clearTokenCache() {
  _cachedToken = null;
  _tokenExpiry = 0;
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

  async getMode(): Promise<{ mode: "demo" | "live"; model: string | null }> {
    const res = await fetch(`${API_BASE}/api/mode`);
    if (!res.ok) {
      return { mode: "demo", model: null };
    }
    return res.json();
  },

  getApiBase() {
    return API_BASE;
  },

  getAuthToken,
};
