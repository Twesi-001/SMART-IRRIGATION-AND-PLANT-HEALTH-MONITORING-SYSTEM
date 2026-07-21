import React from 'react';
import { PowerIcon } from '@heroicons/react/24/outline';

interface PumpControlProps {
  status: 'ON' | 'OFF' | 'UNKNOWN';
  onToggle: () => void;
  loading?: boolean;
  irrigationNeeded?: boolean;   
  canToggleOn?: boolean;        
  message?: string;           
  soilMoisture?: number;        
  threshold?: number;           
}

const PumpControl: React.FC<PumpControlProps> = ({ 
  status, 
  onToggle, 
  loading = false,
  irrigationNeeded = true,
  canToggleOn = true,
  message = '',
  soilMoisture,
  threshold
}) => {
  const isOn = status === 'ON';
  const isLocked = !canToggleOn && !isOn;

  return (
    <div className="bg-white rounded-lg shadow p-4 sm:p-6">
      <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-3 sm:mb-4 text-center">
        Pump Control
      </h3>
      
      <div className="flex flex-col items-center py-2 sm:py-4">
        <div className="relative">
          <div className={`w-16 h-16 sm:w-24 sm:h-24 rounded-full flex items-center justify-center transition-all duration-300 ${
            isOn ? 'bg-green-100 ring-4 ring-green-500' : 
            isLocked ? 'bg-gray-100 ring-4 ring-yellow-400' :
            'bg-gray-100 ring-4 ring-gray-300'
          }`}>
            <PowerIcon className={`h-8 w-8 sm:h-12 sm:w-12 ${
              isOn ? 'text-green-600' : 
              isLocked ? 'text-yellow-500' : 'text-gray-500'
            }`} />
          </div>
          <div className={`absolute -top-2 -right-2 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-full text-[10px] sm:text-xs font-bold ${
            isOn ? 'bg-green-500 text-white' : 
            isLocked ? 'bg-yellow-500 text-white' : 'bg-gray-500 text-white'
          }`}>
            {isOn ? 'ON' : isLocked ? '🔒 LOCKED' : 'OFF'}
          </div>
        </div>

        {/* ✅ Show lock message */}
        {isLocked && (
          <div className="mt-2 text-xs text-yellow-600 text-center max-w-xs">
            🔒 Pump is locked OFF because soil moisture is above threshold.
            <br />
            <span className="text-green-600 font-medium">✅ No irrigation needed.</span>
            {soilMoisture !== undefined && threshold !== undefined && (
              <><br /><span className="text-gray-500">Soil: {soilMoisture}% | Threshold: {threshold}%</span></>
            )}
          </div>
        )}

        {/* ✅ Show irrigation needed message */}
        {!isLocked && irrigationNeeded && !isOn && (
          <div className="mt-2 text-xs text-yellow-600 text-center">
            ⚠️ Irrigation needed! Click below to turn pump ON.
          </div>
        )}

        {/* ✅ Show status message */}
        {message && !isLocked && (
          <p className="text-xs text-gray-400 mt-1 text-center max-w-xs">
            {message}
          </p>
        )}

        <button
          onClick={onToggle}
          disabled={loading || isLocked}
          className={`mt-3 sm:mt-4 px-4 sm:px-6 py-1.5 sm:py-2 rounded-lg font-medium text-white transition-all w-full sm:w-auto ${
            isOn
              ? 'bg-red-600 hover:bg-red-700'
              : isLocked
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700'
          } disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base`}
        >
          {loading ? 'Toggling...' : 
           isOn ? 'Turn OFF' : 
           isLocked ? '🔒 Locked (Moisture OK)' : 'Turn ON'}
        </button>

        <p className="text-xs sm:text-sm text-gray-500 mt-2">
          {isOn ? 'Pump is running' : 
           isLocked ? 'Pump locked OFF' : 
           'Pump is idle'}
        </p>
      </div>
    </div>
  );
};

export default PumpControl;