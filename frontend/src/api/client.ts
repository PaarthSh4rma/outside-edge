const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export class ApiConfigurationError extends Error {
  constructor() {
    super("VITE_API_BASE_URL is not configured.");
    this.name = "ApiConfigurationError";
  }
}

export class ApiError extends Error {
  status: number;

  constructor(status: number) {
    super(`API request failed: ${status}`);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`);

  if (!response.ok) {
    throw new ApiError(response.status);
  }

  return response.json() as Promise<T>;
}

export async function apiPost<T = unknown>(
  path: string,
  body: unknown,
): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new ApiError(response.status);
  }

  return response.json() as Promise<T>;
}

function getApiBaseUrl() {
  if (!API_BASE_URL) {
    throw new ApiConfigurationError();
  }

  return API_BASE_URL.replace(/\/$/, "");
}
