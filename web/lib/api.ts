const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiOptions {
  method?: string;
  body?: any;
  token?: string | null;
}

async function api<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { method = 'GET', body, token } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || 'API Error');
  }

  return data;
}

// Auth
export async function signup(email: string, password: string, name?: string) {
  return api<{ token: string; user: any }>('/api/auth/signup', {
    method: 'POST',
    body: { email, password, name },
  });
}

export async function login(email: string, password: string) {
  return api<{ token: string; user: any }>('/api/auth/login', {
    method: 'POST',
    body: { email, password },
  });
}

export async function logout(token: string) {
  return api('/api/auth/logout', { method: 'POST', token });
}

export async function getMe(token: string) {
  return api<any>('/api/auth/me', { token });
}

export async function betaSignup(email: string, name?: string, interest?: string) {
  return api<{ message: string }>('/api/auth/beta-signup', {
    method: 'POST',
    body: { email, name, interest },
  });
}

// Agents
export async function getPresets() {
  return api<{ personalities: any; voices: any }>('/api/maiai/presets');
}

export async function birthAgent(
  token: string,
  data: {
    name: string;
    personality: string;
    voice_preset?: string;
    custom_traits?: string[];
    custom_prompt?: string;
  }
) {
  return api<any>('/api/maiai/birth', {
    method: 'POST',
    token,
    body: data,
  });
}

export async function getAgents(token: string) {
  return api<any[]>('/api/maiai/agents', { token });
}

export async function getAgent(token: string, id: number) {
  return api<any>(`/api/maiai/agents/${id}`, { token });
}

export async function chatWithAgent(
  token: string,
  agentId: number,
  message: string,
  context?: any[]
) {
  return api<{ response: string; agent_name: string }>(`/api/maiai/agents/${agentId}/chat`, {
    method: 'POST',
    token,
    body: { message, context },
  });
}

export async function retireAgent(token: string, id: number) {
  return api(`/api/maiai/agents/${id}`, { method: 'DELETE', token });
}

// Billing
export async function getTiers() {
  return api<{ tiers: any }>('/api/billing/tiers');
}

export async function getBillingStatus(token: string) {
  return api<any>('/api/billing/status', { token });
}
