/* eslint-disable react-hooks/immutability */
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
import { cropTypes, cropThresholds } from '../constants/cropTypes';

interface Farmer {
  user: {
    id: number;
    username: string;
    email: string | null;
    role: string;
    created_at: string;
  };
  node_count: number;
  nodes: SensorNode[];
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(null);
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [allNodes, setAllNodes] = useState<SensorNode[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<number | null>(null);
  const [favorites, setFavorites] = useState<number[]>(() => {
    const saved = localStorage.getItem('favoriteNodes');
    return saved ? JSON.parse(saved) : [];
  });
  const [refreshing, setRefreshing] = useState(false);
  const [showFarmersList, setShowFarmersList] = useState(false);
  const [farmers, setFarmers] = useState<Farmer[]>([]);
  const [showRecommendForm, setShowRecommendForm] = useState(false);
  const [recommendation, setRecommendation] = useState({
    farmer_id: 0,
    node_id: 0,
    message: ''
  });
  // State for the "Add Garden" form
  const [cropType, setCropType] = useState('');
  const [nodeName, setNodeName] = useState('');
  const [showAddGardenForm, setShowAddGardenForm] = useState(false);

  const previousAlertsRef = useRef<Alert[]>([]);

  const isExtensionOfficer = user?.role === 'extension_officer' || user?.role === 'admin';
  const isFarmer = user?.role === 'farmer';

  // Load initial node
  useEffect(() => {
    const loadInitialNode = async () => {
      try {
        const response = await nodeService.getAll();
        const nodes = response.data;
        setAllNodes(nodes);

        // Filter nodes for farmers
        let userNodes = nodes;
        if (user?.role === 'farmer') {
          userNodes = nodes.filter((n) => n.user_id === user.id);
        }

        if (userNodes.length === 0) {
          setLoading(false);
          setSelectedNodeId(null);
          return;
        }

        const favoriteNode = userNodes.find((n) => favorites.includes(n.id));
        const initialNode = favoriteNode || userNodes[0];
        setSelectedNodeId(initialNode.id);
        await fetchData(initialNode.id);
        setLoading(false);
      } catch (error) {
        console.error('Error loading initial node:', error);
        setLoading(false);
      }
    };

    loadInitialNode();

    if (isExtensionOfficer) {
      fetchFarmers();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
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
  const cropIcons: Record<string, string> = {
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

  // Role badge color
  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-purple-100 text-purple-700';
      case 'extension_officer': return 'bg-blue-100 text-blue-700';
      default: return 'bg-green-100 text-green-700';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'admin': return '🔧 Admin';
      case 'extension_officer': return '👨‍🏫 Extension Officer';
      default: return '👨‍🌾 Farmer';
    }
  };
  async function createNode(nodeName: string, cropType: string, _threshold: number) {
    try {
      const token = localStorage.getItem('token');

      const allNodesResponse = await fetch('https://smart-irrigation-and-plant-health.onrender.com/api/nodes/all', {
        headers: { 'X-API-Key': 'PbCg3h3T0NzuNlg7Bq1YBurjIRwBFYS9908eTksmO7g' }
      });
      const allNodes = await allNodesResponse.json();

      const existingNode = allNodes.find((n: { crop_type: string }) => n.crop_type === cropType);

      if (!existingNode) {
        toast.error(`No node found for crop: ${cropType}`);
        return;
      }

      const response = await fetch('https://smart-irrigation-and-plant-health.onrender.com/api/nodes/select', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          node_id: existingNode.id,
          custom_name: nodeName,
          location: 'Mbarara, Uganda'
        })
      });

      if (response.ok) {
        toast.success('✅ Garden selected successfully!');
        setShowAddGardenForm(false);
        setCropType('');
        setNodeName('');

        // ✅ Simple reload - avoids all routing issues
        window.location.reload();
      } else {
        const error = await response.json();
        toast.error(error.error || 'Failed to select garden');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error selecting garden');
    }
  }
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

  const fetchFarmers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('https://smart-irrigation-and-plant-health.onrender.com/api/users/farmers', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setFarmers(data);
      setShowFarmersList(true);
    } catch (error) {
      toast.error('Failed to load farmers');
    }
  };

  const handleViewFarmer = (farmer: Farmer) => {
    if (farmer.nodes.length > 0) {
      handleNodeSelect(farmer.nodes[0].id);
      setShowFarmersList(false);
      toast.success(`Viewing ${farmer.user.username}'s garden`);
    } else {
      toast(`${farmer.user.username} has no gardens yet`, { icon: 'ℹ️' });
    }
  };

  const handleSendRecommendation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('https://smart-irrigation-and-plant-health.onrender.com/api/alerts/recommend', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          farmer_id: Number(recommendation.farmer_id),
          node_id: Number(recommendation.node_id),
          message: recommendation.message
        })
      });

      if (response.ok) {
        toast.success('Recommendation sent successfully!');
        setShowRecommendForm(false);
        setRecommendation({ farmer_id: 0, node_id: 0, message: '' });
        if (selectedNodeId) {
          await fetchData(selectedNodeId);
        }
        if (showFarmersList) {
          await fetchFarmers();
        }
      } else {
        toast.error('Failed to send recommendation');
      }
    } catch (error) {
      toast.error('Error sending recommendation');
    }
  };

  const handleNodeSelect = (nodeId: number) => {
    setSelectedNodeId(nodeId);
    setLoading(true);
    fetchData(nodeId);
  };

  const handleToggleFavorite = (nodeId: number) => {
    setFavorites((prev) => {
      if (prev.includes(nodeId)) {
        return prev.filter((id) => id !== nodeId);
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

        // Filter nodes that belong to the current user (for farmers)
        let userNodes = nodes;
        if (user?.role === 'farmer') {
          userNodes = nodes.filter((n) => n.user_id === user.id);
        }

        if (userNodes.length === 0) {
          setLoading(false);
          setSelectedNodeId(null);
          return;
        }

        const favoriteNode = userNodes.find((n) => favorites.includes(n.id));
        const initialNode = favoriteNode || userNodes[0];
        setSelectedNodeId(initialNode.id);
        await fetchData(initialNode.id);
        setLoading(false);
      } catch (error) {
        console.error('Error loading initial node:', error);
        setLoading(false);
      }
    };
    loadInitialNode();

    if (isExtensionOfficer) {
      fetchFarmers();
    }
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
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="text-base sm:text-xl text-gray-600">🌱 No gardens found</div>
        <p className="text-sm text-gray-400 mt-2">Create a new garden to get started</p>

        <div className="mt-4 bg-white p-6 rounded-lg shadow-md w-full max-w-md">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Add New Garden</h3>
          <form onSubmit={async (e) => {
            e.preventDefault();
            if (nodeName.trim() && cropType) {
              await createNode(nodeName.trim(), cropType, cropThresholds[cropType]);
            }
          }}>
            <div className="mb-3">
              <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="garden-name">
                Garden Name
              </label>
              <input
                id="garden-name"
                type="text"
                value={nodeName}
                onChange={(e) => setNodeName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="e.g., My Garden"
                required
              />
            </div>

            <div className="mb-3">
              <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="crop-select">
                Crop Type
              </label>
              <select
                id="crop-select"
                value={cropType}
                onChange={(e) => setCropType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                required
              >
                <option value="">Select a crop</option>
                {cropTypes.map((crop) => (
                  <option key={crop} value={crop}>
                    {crop} (Threshold: {cropThresholds[crop]}%)
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              Create Garden
            </button>
          </form>
        </div>
      </div>
    );
  }

  const { node, latest_reading, statistics, pump_status } = dashboardData;
  const favoriteNodes = allNodes.filter((n) => favorites.includes(n.id));

  const farmerNodes = allNodes.filter((n) => n.user_id === recommendation.farmer_id);

  return (
    <div>
      {/* Header with Role Badge */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4 sm:mb-6">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-xl sm:text-2xl font-bold text-gray-800">Dashboard</h1>
            <span className={`px-2 py-1 text-xs rounded-full ${getRoleBadgeColor(user?.role || 'farmer')}`}>
              {getRoleLabel(user?.role || 'farmer')}
            </span>
          </div>
          <p className="text-sm sm:text-base text-gray-600 truncate max-w-[200px] sm:max-w-none">
            {node.node_name} - {node.location}
          </p>
        </div>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 w-full sm:w-auto">
          {/* ✅ Add Garden button - ONLY for farmers (all farmers, with or without gardens) */}
          {isFarmer && (
            <button
              onClick={() => setShowAddGardenForm(!showAddGardenForm)}
              className="w-full sm:w-auto bg-green-600 text-white px-3 sm:px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm flex items-center gap-1"
            >
              {showAddGardenForm ? '✕ Close' : '➕ Add Garden'}
            </button>
          )}
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

      {/* ✅ Add Garden Form - ONLY for farmers */}
      {isFarmer && showAddGardenForm && (
        <div className="mb-6 bg-white rounded-lg shadow p-4">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-semibold text-gray-800">🌱 Add New Garden</h3>
            <button
              onClick={() => {
                setShowAddGardenForm(false);
                setCropType('');
                setNodeName('');
              }}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
          <form onSubmit={async (e) => {
            e.preventDefault();
            if (nodeName.trim() && cropType) {
              await createNode(nodeName.trim(), cropType, cropThresholds[cropType]);
            }
          }}>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="garden-name">
                  Garden Name
                </label>
                <input
                  id="garden-name"
                  type="text"
                  value={nodeName}
                  onChange={(e) => setNodeName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="e.g., My Garden"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="crop-select">
                  Crop Type
                </label>
                <select
                  id="crop-select"
                  value={cropType}
                  onChange={(e) => setCropType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  required
                >
                  <option value="">Select a crop</option>
                  {cropTypes.map((crop) => (
                    <option key={crop} value={crop}>
                      {crop} (Threshold: {cropThresholds[crop]}%)
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="mt-3 flex gap-2">
              <button
                type="submit"
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 text-sm"
              >
                Create Garden
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowAddGardenForm(false);
                  setCropType('');
                  setNodeName('');
                }}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 text-sm"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Extension Officer / Admin: View All Farmers Button */}
      {isExtensionOfficer && (
        <div className="mb-4 flex flex-wrap gap-2">
          <button
            onClick={() => {
              fetchFarmers();
              setShowFarmersList(true);
            }}
            className="w-full sm:w-auto bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            👨‍🌾 View All Farmers
          </button>
          <button
            onClick={() => setShowRecommendForm(true)}
            className="w-full sm:w-auto bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm"
          >
            📝 Send Recommendation
          </button>
        </div>
      )}

      {/* Recommendation Form */}
      {showRecommendForm && isExtensionOfficer && (
        <div className="mb-6 bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-semibold mb-3">📝 Send Recommendation</h3>
          <form onSubmit={handleSendRecommendation}>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="farmer-select">
                  Farmer
                </label>
                <select
                  id="farmer-select"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={recommendation.farmer_id}
                  onChange={(e) => setRecommendation({ ...recommendation, farmer_id: Number(e.target.value) })}
                  required
                >
                  <option value={0}>Select farmer</option>
                  {farmers.map((farmer) => (
                    <option key={farmer.user.id} value={farmer.user.id}>
                      {farmer.user.username}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="node-select">
                  Garden
                </label>
                <select
                  id="node-select"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={recommendation.node_id}
                  onChange={(e) => setRecommendation({ ...recommendation, node_id: Number(e.target.value) })}
                  required
                >
                  <option value={0}>Select garden</option>
                  {farmerNodes.map((node) => (
                    <option key={node.id} value={node.id}>
                      {node.node_name} ({node.crop_type})
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="mb-3">
              <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="message-textarea">
                Message
              </label>
              <textarea
                id="message-textarea"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                rows={3}
                value={recommendation.message}
                onChange={(e) => setRecommendation({ ...recommendation, message: e.target.value })}
                placeholder="Enter your recommendation for the farmer..."
                required
              />
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 text-sm"
              >
                Send Recommendation
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowRecommendForm(false);
                  setRecommendation({ farmer_id: 0, node_id: 0, message: '' });
                }}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 text-sm"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Farmers List (Extension Officer / Admin) */}
      {showFarmersList && isExtensionOfficer && (
        <div className="mb-6 bg-white rounded-lg shadow p-4 overflow-x-auto">
          <h3 className="text-lg font-semibold mb-3">All Farmers</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Farmer</th>
                <th className="text-left py-2">Gardens</th>
                <th className="text-left py-2">Status</th>
                <th className="text-left py-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {farmers.map((farmer) => (
                <tr key={farmer.user.id} className="border-b hover:bg-gray-50">
                  <td className="py-2">{farmer.user.username}</td>
                  <td className="py-2">{farmer.node_count}</td>
                  <td className="py-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${farmer.node_count > 0 ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                      }`}>
                      {farmer.node_count > 0 ? '✅ Active' : '❌ No gardens'}
                    </span>
                  </td>
                  <td className="py-2">
                    <button
                      onClick={() => handleViewFarmer(farmer)}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button
            onClick={() => setShowFarmersList(false)}
            className="mt-3 text-gray-500 hover:text-gray-700 text-sm"
          >
            Close
          </button>
        </div>
      )}

      {/* Favorite Nodes Grid - Only for Farmers */}
      {!isExtensionOfficer && favoriteNodes.length > 0 && (
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
                className={`cursor-pointer p-3 rounded-lg border-2 transition-all ${selectedNodeId === n.id
                  ? 'border-green-500 bg-green-50 shadow-md'
                  : 'border-gray-200 bg-white hover:border-green-300 hover:shadow'
                  }`}
              >
                <div className="text-2xl text-center">{getCropIcon(n.crop_type)}</div>
                <div className="text-center mt-1">
                  <p className="text-sm font-medium text-gray-800 truncate">{n.node_name}</p>
                  <p className="text-xs text-gray-500">{n.crop_type || 'Unknown'}</p>
                  <p className="text-xs text-gray-400 mt-0.5">Threshold: {n.moisture_threshold}%</p>
                  <span className={`inline-block mt-1 px-2 py-0.5 text-xs rounded-full ${n.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
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
          {user?.role === 'farmer' ? (
            (() => {
              // Calculate irrigation status
              const threshold = node?.moisture_threshold || 35;
              const currentMoisture = latest_reading?.soil_moisture || 0;
              const irrigationNeeded = currentMoisture < threshold;
              const canToggleOn = irrigationNeeded;

              return (
                <PumpControl
                  status={pump_status}
                  onToggle={handleTogglePump}
                  irrigationNeeded={irrigationNeeded}
                  canToggleOn={canToggleOn}
                  soilMoisture={currentMoisture}
                  threshold={threshold}
                  message={irrigationNeeded
                    ? "Soil is dry. Turn pump ON if needed."
                    : `Soil moisture (${currentMoisture}%) is above threshold (${threshold}%). Pump locked OFF.`}
                />
              );
            })()
          ) : (
            <div className="bg-gray-100 rounded-lg shadow p-4 text-center text-gray-500">
              <p className="text-sm">🔒 Pump control is only available for farmers</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;