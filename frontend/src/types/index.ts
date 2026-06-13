export interface AlertData {
  name: string;
  service: string;
  severity: string;
  metric_value: number;
  threshold: number;
  alert_time: string;
}

export interface Recommendation {
  step: number;
  action: string;
  risk: 'Low' | 'Medium' | 'High';
  priority: 'Low' | 'Medium' | 'High';
}

export interface TimelineEvent {
  time: string;
  event: string;
}

export interface Incident {
  id: string;
  title: string;
  status: 'Triggered' | 'Investigating' | 'RCA Found' | 'Knowledge Retrieved' | 'Resolution Generated' | 'Mitigating' | 'Resolved';
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  confidence_score: number;
  alert_data?: AlertData;
  metrics?: {
    cpu?: number;
    memory?: number;
    latency?: number;
    error_rate?: number;
    connections?: number;
    disk_util?: number;
    [key: string]: number | undefined;
  };
  logs?: string[];
  findings?: string[];
  root_cause?: string;
  recommendations?: Recommendation[];
  executive_report?: string;
  timeline?: TimelineEvent[];
  reasoning_trace?: string[];
  created_at: string;
  updated_at: string;
}

export interface AgentExecutionHistory {
  incident_id: string;
  status: 'Running' | 'Completed' | 'Failed';
  duration: string;
  timestamp: string;
}

export interface AgentStatus {
  name: string;
  status: 'idle' | 'executing' | 'failed';
  current_task: string;
  total_executions: number;
  avg_response_time: string;
  confidence: string;
  history: AgentExecutionHistory[];
}

export interface SimulationResponse {
  action: string;
  success_probability: number;
  downtime_estimate: string;
  risk_estimate: string;
  recovery_estimate: string;
}

export interface KPIStats {
  active_incidents: number;
  critical_alerts: number;
  mttr: string;
  ai_confidence: string;
}

export interface AnalyticsData {
  kpis: KPIStats;
  trends: Array<{ date: string; incidents: number; resolved: number }>;
  root_causes: Array<{ name: string; value: number }>;
  resolution_times: Array<{ category: string; time: number }>;
  agent_speeds: Array<{ agent: string; duration: number }>;
}
