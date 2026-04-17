import { API_BASE_URL } from "./config";

const buildUrl = (path) => {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
};

const parseResponse = async (response) => {
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return null;
  }

  return response.json();
};

const request = async (method, path, options = {}) => {
  const { body, headers = {}, token, signal } = options;
  const isFormData = body instanceof FormData;

  const response = await fetch(buildUrl(path), {
    method,
    credentials: "include",
    signal,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body === undefined ? undefined : isFormData ? body : JSON.stringify(body),
  });

  const payload = await parseResponse(response);
  if (!response.ok) {
    const error = new Error(payload?.error?.message || payload?.message || `HTTP ${response.status}`);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }

  return payload;
};

export const httpClient = {
  get: (path, options) => request("GET", path, options),
  post: (path, body, options = {}) => request("POST", path, { ...options, body }),
  put: (path, body, options = {}) => request("PUT", path, { ...options, body }),
  patch: (path, body, options = {}) => request("PATCH", path, { ...options, body }),
  delete: (path, options) => request("DELETE", path, options),
};
