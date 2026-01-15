/**
 * API client for SaltShark backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Minions API
 */
export const minionsAPI = {
  list: () => fetchAPI<any>("/api/v1/minions"),
  get: (minionId: string) => fetchAPI<any>(`/api/v1/minions/${minionId}`),
  getGrains: (minionId: string) =>
    fetchAPI<any>(`/api/v1/minions/${minionId}/grains`),
  getPillars: (minionId: string) =>
    fetchAPI<any>(`/api/v1/minions/${minionId}/pillars`),
};

/**
 * Jobs API
 */
export const jobsAPI = {
  list: () => fetchAPI<any>("/api/v1/jobs"),
  get: (jid: string) => fetchAPI<any>(`/api/v1/jobs/${jid}`),
  execute: (data: any) =>
    fetchAPI<any>("/api/v1/jobs/execute", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

/**
 * Keys API
 */
export const keysAPI = {
  list: () => fetchAPI<any>("/api/v1/keys"),
  accept: (minionId: string) =>
    fetchAPI<any>(`/api/v1/keys/${minionId}/accept`, { method: "POST" }),
  reject: (minionId: string) =>
    fetchAPI<any>(`/api/v1/keys/${minionId}/reject`, { method: "POST" }),
  delete: (minionId: string) =>
    fetchAPI<any>(`/api/v1/keys/${minionId}`, { method: "DELETE" }),
};

/**
 * Schedules API
 */
export const schedulesAPI = {
  list: (target: string = "*") => fetchAPI<any>(`/api/v1/schedules/${target}`),
  create: (data: any) =>
    fetchAPI<any>("/api/v1/schedules", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  delete: (target: string, name: string) =>
    fetchAPI<any>(`/api/v1/schedules/${target}/${name}`, {
      method: "DELETE",
    }),
};

/**
 * Health check
 */
export const healthAPI = {
  check: () => fetchAPI<{ status: string }>("/health"),
};
