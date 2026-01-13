/**
 * API client for SaltShark backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
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
  list: () => fetchAPI<any>('/api/v1/minions'),
  get: (minionId: string) => fetchAPI<any>(`/api/v1/minions/${minionId}`),
  getGrains: (minionId: string) => fetchAPI<any>(`/api/v1/minions/${minionId}/grains`),
  getPillars: (minionId: string) => fetchAPI<any>(`/api/v1/minions/${minionId}/pillars`),
};

/**
 * Jobs API
 */
export const jobsAPI = {
  list: () => fetchAPI<any>('/api/v1/jobs'),
  get: (jid: string) => fetchAPI<any>(`/api/v1/jobs/${jid}`),
  execute: (data: any) => fetchAPI<any>('/api/v1/jobs/execute', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};

/**
 * Health check
 */
export const healthAPI = {
  check: () => fetchAPI<{ status: string }>('/health'),
};
