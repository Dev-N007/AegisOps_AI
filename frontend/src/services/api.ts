import { Incident, AgentStatus, SimulationResponse, AnalyticsData } from '../types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => 'Unknown Error');
    throw new Error(`API Error on ${path} (${response.status}): ${errorText}`);
  }

  return response.json() as Promise<T>;
}

export const api = {
  getIncidents: () => fetchApi<Incident[]>('/incidents'),
  
  getIncident: (id: string) => fetchApi<Incident>(`/incidents/${id}`),
  
  diagnoseIncident: (id: string) => fetchApi<{ status: string; message: string }>(`/incidents/${id}/diagnose`, {
    method: 'POST',
  }),
  
  getAgents: () => fetchApi<AgentStatus[]>('/agents'),
  
  simulateAction: (action: string, incidentId: string) => 
    fetchApi<SimulationResponse>('/simulate', {
      method: 'POST',
      body: JSON.stringify({ action, incident_id: incidentId }),
    }),
    
  getAnalytics: () => fetchApi<AnalyticsData>('/analytics'),
};
