/* eslint-disable @typescript-eslint/no-unused-vars */
import React from 'react';
import { Alert } from '../types';
import { alertService } from '../services/api';
import toast from 'react-hot-toast';
import { ExclamationTriangleIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

interface AlertsListProps {
  alerts: Alert[];
  onResolve?: () => void;
}

const AlertsList: React.FC<AlertsListProps> = ({ alerts, onResolve }) => {
  const handleResolve = async (alertId: number) => {
    try {
      await alertService.resolve(alertId);
      toast.success('Alert resolved!');
      if (onResolve) onResolve();
    } catch (error) {
      toast.error('Failed to resolve alert');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-red-50 border-l-4 border-red-500 text-red-800';
      case 'WARNING':
        return 'bg-yellow-50 border-l-4 border-yellow-500 text-yellow-800';
      case 'INFO':
        return 'bg-blue-50 border-l-4 border-blue-500 text-blue-800';
      default:
        return 'bg-gray-50 border-l-4 border-gray-400 text-gray-800';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return <XCircleIcon className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />;
      case 'WARNING':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500 flex-shrink-0 mt-0.5" />;
      case 'INFO':
        return <CheckCircleIcon className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-500 flex-shrink-0 mt-0.5" />;
    }
  };

  // Format time in Uganda local time (UTC+3)
  const formatLocalTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-UG', {
      timeZone: 'Africa/Kampala',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
        <ExclamationTriangleIcon className="h-5 w-5 mr-2 text-yellow-500" />
        Alerts
        <span className="ml-2 text-sm font-normal text-gray-500">({alerts.length})</span>
      </h3>

      {alerts.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <CheckCircleIcon className="h-12 w-12 mx-auto text-green-500 mb-2" />
          <p className="text-base">No active alerts</p>
          <p className="text-sm text-gray-400">All systems normal ✅</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-3 rounded-lg shadow-sm ${getSeverityColor(alert.severity)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  {getSeverityIcon(alert.severity)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-semibold">{alert.alert_type}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full bg-white/50`}>
                        {alert.severity}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatLocalTime(alert.created_at)}
                      </span>
                    </div>
                    <p className="text-sm mt-0.5">{alert.message}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleResolve(alert.id)}
                  className="ml-2 px-3 py-1 text-xs font-medium text-white bg-green-600 rounded-md hover:bg-green-700 transition-colors whitespace-nowrap"
                >
                  Resolve
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AlertsList;