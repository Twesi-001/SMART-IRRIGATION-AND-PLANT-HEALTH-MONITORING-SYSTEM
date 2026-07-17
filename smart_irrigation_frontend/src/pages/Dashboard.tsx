/* eslint-disable react-hooks/set-state-in-effect */
/* eslint-disable @typescript-eslint/no-unused-vars */
import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { dashboardService, readingsService, pumpService, alertService } from '../services/api';
import { DashboardSummary, SensorReading, Alert } from '../types';
import toast from 'react-hot-toast';
import StatCard from '../components/StatCard';
import SensorGauge from '../components/SensorGauge';
import AlertsList from '../components/AlertsList';
import PumpControl from '../components/PumpControl';
import ChartComponent from '../components/ChartComponent';

const Dashboard: React.FC = () => {
  useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(null);
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  
  // Track previous alerts for toast notifications
  const previousAlertsRef = useRef<Alert[]>([]);

  // Format time in Uganda local time (UTC+3)
const formatLocalTime = (dateString: string) => {
  const date = new Date(dateString);
  // Add 3 hours for Uganda time (UTC+3)
  date.setHours(date.getHours() + 3);
  return date.toLocaleString('en-UG', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true // ← This adds AM/PM
  });
};
  const fetchData = async () => {
    try {
      const [dashboardRes, readingsRes, alertsRes] = await Promise.all([
        dashboardService.getSummary(1),
        readingsService.getReadings(1, 20),
        alertService.getUnresolved(1),
      ]);

      setDashboardData(dashboardRes.data);
      setReadings(readingsRes.data);
      
      // Check for new alerts before updating state
      const newAlerts = alertsRes.data;
      const oldAlerts = previousAlertsRef.current;
      
      // Find new alerts (alerts that weren't there before)
      if (newAlerts.length > 0 && oldAlerts.length > 0) {
        const addedAlerts = newAlerts.filter(
          alert => !oldAlerts.some(prev => prev.id === alert.id)
        );
        
        // Show toast for each new alert
        addedAlerts.forEach((alert: Alert) => {
          const severityColors = {
            CRITICAL: 'bg-red-100 text-red-800 border-red-500',
            WARNING: 'bg-yellow-100 text-yellow-800 border-yellow-500',
            INFO: 'bg-blue-100 text-blue-800 border-blue-500',
          };
          
          const colorClass = severityColors[alert.severity as keyof typeof severityColors] || 'bg-gray-100 border-gray-500';
          
          toast.custom((t) => (
            <div
              className={`max-w-sm w-full shadow-lg rounded-lg border-l-4 ${colorClass} p-4`}
            >
              <div className="flex items-start">
                <div className="flex-1">
                  <p className="text-sm font-bold">{alert.alert_type}</p>
                  <p className="text-sm">{alert.message}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {alert.severity} • {formatLocalTime(alert.created_at)}
                  </p>
                </div>
                <button
                  onClick={() => toast.dismiss(t.id)}
                  className="ml-4 text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
            </div>
          ), {
            duration: 5000,
            position: 'top-right',
          });
        });
      }
      
      // Update alerts state
      setAlerts(newAlerts);
      // Update previous alerts ref
      previousAlertsRef.current = newAlerts;
      
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      fetchData();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
    toast.success('Data refreshed!');
  };

  const handleTogglePump = async () => {
    try {
      await pumpService.toggle(1);
      toast.success('Pump toggled!');
      fetchData();
    } catch (error) {
      toast.error('Failed to toggle pump');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-base sm:text-xl">Loading dashboard...</div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-base sm:text-xl text-red-600">Failed to load dashboard data</div>
      </div>
    );
  }

  const { node, latest_reading, statistics, pump_status } = dashboardData;

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4 sm:mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-sm sm:text-base text-gray-600 truncate max-w-[200px] sm:max-w-none">
            {node.node_name} - {node.location}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="w-full sm:w-auto bg-green-600 text-white px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 text-sm sm:text-base"
        >
          {refreshing ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>

      {/* Stats Cards - Responsive grid */}
      <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-3 md:gap-4 mb-4 sm:mb-6">
        <StatCard
          title="Soil Moisture"
          value={latest_reading ? `${latest_reading.soil_moisture}%` : '--'}
          change={latest_reading ? `${statistics.avg_soil_moisture.toFixed(1)}% avg` : 'No data'}
          color="green"
        />
        <StatCard
          title="Temperature"
          value={latest_reading ? `${latest_reading.temperature}°C` : '--'}
          change={latest_reading ? `${statistics.avg_temperature.toFixed(1)}°C avg` : 'No data'}
          color="red"
        />
        <StatCard
          title="Humidity"
          value={latest_reading ? `${latest_reading.humidity}%` : '--'}
          change={latest_reading ? `${statistics.avg_humidity.toFixed(1)}% avg` : 'No data'}
          color="blue"
        />
        <StatCard
          title="Pump Status"
          value={pump_status}
          change={`${statistics.total_readings} readings`}
          color={pump_status === 'ON' ? 'green' : 'gray'}
        />
      </div>

      {/* Gauges - Responsive */}
      {latest_reading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-6">
          <SensorGauge
            value={latest_reading.soil_moisture}
            max={100}
            label="Soil Moisture"
            color="#22c55e"
            threshold={node.moisture_threshold}
          />
          <SensorGauge
            value={latest_reading.temperature}
            max={50}
            label="Temperature"
            color="#ef4444"
          />
          <SensorGauge
            value={latest_reading.humidity}
            max={100}
            label="Humidity"
            color="#3b82f6"
          />
        </div>
      )}

      {/* Chart - Full width on all screens */}
      <div className="bg-white p-3 sm:p-4 rounded-lg shadow mb-4 sm:mb-6">
        <ChartComponent readings={readings} title="Sensor History" />
      </div>

      {/* Alerts and Pump Control - Responsive layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6" id="alerts-section">
        <div className="lg:col-span-2">
          <AlertsList alerts={alerts} onResolve={fetchData} />
        </div>
        <div>
          <PumpControl
            status={pump_status}
            onToggle={handleTogglePump}
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;