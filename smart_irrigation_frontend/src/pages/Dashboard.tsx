/* eslint-disable @typescript-eslint/no-unused-vars */
import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { dashboardService, readingsService, pumpService, alertService, nodeService } from '../services/api';
import { DashboardSummary, SensorReading, Alert, SensorNode } from '../types';
import toast from 'react-hot-toast';
import StatCard from '../components/StatCard';
import SensorGauge from '../components/SensorGauge';
import AlertsList from '../components/AlertsList';
import PumpControl from '../components/PumpControl';
import ChartComponent from '../components/ChartComponent';
import NodeSelector from '../components/NodeSelector';

const Dashboard: React.FC = () => {
  useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(null);
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [allNodes, setAllNodes] = useState<SensorNode[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<number | null>(null);
  const [favorites, setFavorites] = useState<number[]>(() => {
    // Load favorites from localStorage
    const saved = localStorage.getItem('favoriteNodes');
    return saved ? JSON.parse(saved) : [];
  });
  const [refreshing, setRefreshing] = useState(false);
  
  // Track previous alerts for toast notifications
  const previousAlertsRef = useRef<Alert[]>([]);

  // Save favorites to localStorage when they change
  useEffect(() => {
    localStorage.setItem('favoriteNodes', JSON.stringify(favorites));
  }, [favorites]);

  // Format time in Uganda local time (UTC+3)
  const formatLocalTime = (dateString: string) => {
    const date = new Date(dateString);
    date.setHours(date.getHours() + 3);
    return date.toLocaleString('en-UG', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  // Crop icons mapping
  const cropIcons: { [key: string]: string } = {
    'Maize': '🌽',
    'Tomato': '🍅',
    'Cabbage': '🥬',
    'Onion': '🧅',
    'Mango': '🥭',
    'Banana': '🍌',
    'Pineapple': '🍍',
    'Carrot': '🥕',
    'Capsicum': '🫑',
    'Eggplant': '🍆',
    'Sukuma Wiki': '🥬',
    'Spinach': '🌿',
    'Beans': '🫘',
    'Garlic': '🧄',
    'Strawberry': '🍓',
    'Lettuce': '🥗',
    'Cucumber': '🥒',
    'Watermelon': '🍉',
    'Pumpkin': '🎃',
    'Passion Fruit': '🍈',
  };

  const getCropIcon = (cropType: string | null) => {
    if (!cropType) return '🌱';
    return cropIcons[cropType] || '🌱';
  };

  const fetchData = async (nodeId: number) => {
    try {
      const [dashboardRes, readingsRes, alertsRes, nodesRes] = await Promise.all([
        dashboardService.getSummary(nodeId),
        readingsService.getReadings(nodeId, 20),
        alertService.getUnresolved(nodeId),
        nodeService.getAll(),
      ]);

      setDashboardData(dashboardRes.data);
      setReadings(readingsRes.data);
      setAlerts(alertsRes.data);
      setAllNodes(nodesRes.data);
      
      // Check for new alerts
      const newAlerts = alertsRes.data;
      const oldAlerts = previousAlertsRef.current;
      
      if (newAlerts.length > 0 && oldAlerts.length > 0) {
        const addedAlerts = newAlerts.filter(
          alert => !oldAlerts.some(prev => prev.id === alert.id)
        );
        
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
      
      setAlerts(newAlerts);
      previousAlertsRef.current = newAlerts;
      
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleNodeSelect = (nodeId: number) => {
    setSelectedNodeId(nodeId);
    setLoading(true);
    fetchData(nodeId);
  };

  const handleToggleFavorite = (nodeId: number) => {
    setFavorites(prev => {
      if (prev.includes(nodeId)) {
        return prev.filter(id => id !== nodeId);
      } else {
        return [...prev, nodeId];
      }
    });
  };

  // Load initial node
  useEffect(() => {
    const loadInitialNode = async () => {
      try {
        const response = await nodeService.getAll();
        const nodes = response.data;
        setAllNodes(nodes);
        
        if (nodes.length > 0) {
          // Try to select the first favorite, or the first node
          const favoriteNode = nodes.find(n => favorites.includes(n.id));
          const initialNode = favoriteNode || nodes[0];
          setSelectedNodeId(initialNode.id);
          await fetchData(initialNode.id);
        }
        setLoading(false);
      } catch (error) {
        console.error('Error loading initial node:', error);
        setLoading(false);
      }
    };
    loadInitialNode();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleRefresh = async () => {
    if (selectedNodeId === null) return;
    setRefreshing(true);
    await fetchData(selectedNodeId);
    setRefreshing(false);
    toast.success('Data refreshed!');
  };

  const handleTogglePump = async () => {
    if (selectedNodeId === null) return;
    try {
      await pumpService.toggle(selectedNodeId);
      toast.success('Pump toggled!');
      fetchData(selectedNodeId);
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

  if (!dashboardData || selectedNodeId === null) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-base sm:text-xl text-red-600">Failed to load dashboard data</div>
      </div>
    );
  }

  const { node, latest_reading, statistics, pump_status } = dashboardData;

  // Get favorited nodes
  const favoriteNodes = allNodes.filter(n => favorites.includes(n.id));

  return (
    <div>
      {/* Header with Node Selector */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4 sm:mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-sm sm:text-base text-gray-600 truncate max-w-[200px] sm:max-w-none">
            {node.node_name} - {node.location}
          </p>
        </div>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 w-full sm:w-auto">
          <NodeSelector
            selectedNodeId={selectedNodeId}
            onSelectNode={handleNodeSelect}
            favorites={favorites}
            onToggleFavorite={handleToggleFavorite}
          />
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="w-full sm:w-auto bg-green-600 text-white px-3 sm:px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 text-sm"
          >
            {refreshing ? 'Refreshing...' : 'Refresh Data'}
          </button>
        </div>
      </div>

      {/* Favorite Nodes Grid */}
      {favoriteNodes.length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-700 mb-3 flex items-center">
            ⭐ Your Favorite Gardens
            <span className="ml-2 text-sm font-normal text-gray-500">({favoriteNodes.length})</span>
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {favoriteNodes.map((n) => (
              <div
                key={n.id}
                onClick={() => handleNodeSelect(n.id)}
                className={`cursor-pointer p-3 rounded-lg border-2 transition-all ${
                  selectedNodeId === n.id
                    ? 'border-green-500 bg-green-50 shadow-md'
                    : 'border-gray-200 bg-white hover:border-green-300 hover:shadow'
                }`}
              >
                <div className="text-2xl text-center">{getCropIcon(n.crop_type)}</div>
                <div className="text-center mt-1">
                  <p className="text-sm font-medium text-gray-800 truncate">{n.node_name}</p>
                  <p className="text-xs text-gray-500">{n.crop_type || 'Unknown'}</p>
                  <p className="text-xs text-gray-400 mt-0.5">Threshold: {n.moisture_threshold}%</p>
                  <span className={`inline-block mt-1 px-2 py-0.5 text-xs rounded-full ${
                    n.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                  }`}>
                    {n.is_active ? '✅ Active' : '❌ Inactive'}
                  </span>
                  <div className="mt-1 text-yellow-500">★</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

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
          <AlertsList alerts={alerts} onResolve={() => selectedNodeId && fetchData(selectedNodeId)} />
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