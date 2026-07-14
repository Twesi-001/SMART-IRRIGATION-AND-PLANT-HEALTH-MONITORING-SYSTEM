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
        return 'bg-red-100 border-red-500 text-red-700';
      case 'WARNING':
        return 'bg-yellow-100 border-yellow-500 text-yellow-700';
      case 'INFO':
        return 'bg-blue-100 border-blue-500 text-blue-700';
      default:
        return 'bg-gray-100 border-gray-500 text-gray-700';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return <XCircleIcon className="h-4 w-4 sm:h-5 sm:w-5 text-red-600 flex-shrink-0" />;
      case 'WARNING':
        return <ExclamationTriangleIcon className="h-4 w-4 sm:h-5 sm:w-5 text-yellow-600 flex-shrink-0" />;
      case 'INFO':
        return <CheckCircleIcon className="h-4 w-4 sm:h-5 sm:w-5 text-blue-600 flex-shrink-0" />;
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-3 sm:p-4">
      <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-3 sm:mb-4 flex items-center">
        <ExclamationTriangleIcon className="h-4 w-4 sm:h-5 sm:w-5 mr-2 text-yellow-600" />
        Alerts <span className="ml-2 text-sm font-normal text-gray-500">({alerts.length})</span>
      </h3>

      {alerts.length === 0 ? (
        <div className="text-center py-4 sm:py-8 text-gray-500">
          <CheckCircleIcon className="h-8 w-8 sm:h-12 sm:w-12 mx-auto text-green-500 mb-2" />
          <p className="text-sm sm:text-base">No active alerts</p>
          <p className="text-xs sm:text-sm">All systems normal</p>
        </div>
      ) : (
        <div className="space-y-2 sm:space-y-3 max-h-[300px] sm:max-h-[400px] overflow-y-auto">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-2 sm:p-3 rounded-lg border-l-4 ${getSeverityColor(alert.severity)}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start space-x-2 min-w-0">
                  {getSeverityIcon(alert.severity)}
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-1 sm:gap-2">
                      <span className="text-sm sm:text-base font-medium break-words">{alert.alert_type}</span>
                      <span className="text-[10px] sm:text-xs px-1.5 sm:px-2 py-0.5 rounded-full bg-white bg-opacity-50">
                        {alert.severity}
                      </span>
                    </div>
                    <p className="text-xs sm:text-sm break-words">{alert.message}</p>
                    <p className="text-[10px] sm:text-xs opacity-70 mt-0.5 sm:mt-1">
                      {new Date(alert.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleResolve(alert.id)}
                  className="text-xs sm:text-sm text-green-600 hover:text-green-800 font-medium whitespace-nowrap"
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