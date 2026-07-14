export interface User {
  id: number;
  username: string;
  email: string | null;
  role: string;
  created_at: string;
}

export interface SensorNode {
  id: number;
  node_name: string;
  location: string | null;
  crop_type: string | null;
  moisture_threshold: number;
  is_active: boolean;
}

export interface SensorReading {
  id: number;
  node_id: number;
  soil_moisture: number;
  temperature: number;
  humidity: number;
  recorded_at: string;
}

export interface Prediction {
  id: number;
  reading_id: number;
  irrigation_needed: boolean;
  recommended_action: string;
  confidence: number;
  model_version: string;
  created_at: string;
}

export interface PumpCommand {
  id: number;
  node_id: number;
  command: 'ON' | 'OFF';
  source: 'MANUAL' | 'AUTO';
  issued_by: number | null;
  issued_at: string;
}

export interface Alert {
  id: number;
  node_id: number;
  alert_type: string;
  message: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  resolved: boolean;
  created_at: string;
  resolved_at: string | null;
}

export interface DashboardSummary {
  node: SensorNode;
  latest_reading: SensorReading | null;
  recent_readings: SensorReading[];
  active_alerts: Alert[];
  pump_status: 'ON' | 'OFF' | 'UNKNOWN';
  pump_last_changed: string | null;
  statistics: {
    avg_soil_moisture: number;
    max_soil_moisture: number;
    min_soil_moisture: number;
    avg_temperature: number;
    avg_humidity: number;
    total_readings: number;
  };
  recent_pump_commands: PumpCommand[];
}

export interface LoginResponse {
  access_token: string;
  user: User;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}