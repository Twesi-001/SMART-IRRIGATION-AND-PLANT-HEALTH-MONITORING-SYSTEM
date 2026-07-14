import React from 'react';

interface SensorGaugeProps {
  value: number;
  max: number;
  label: string;
  color: string;
  threshold?: number;
}

const SensorGauge: React.FC<SensorGaugeProps> = ({ value, max, label, color, threshold }) => {
  const percentage = (value / max) * 100;
  const isWarning = threshold && value < threshold;

  return (
    <div className="bg-white p-3 sm:p-4 rounded-lg shadow">
      <div className="flex justify-between items-center mb-1 sm:mb-2">
        <span className="text-xs sm:text-sm font-medium text-gray-700">{label}</span>
        <span className="text-base sm:text-lg font-bold" style={{ color }}>
          {value}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 sm:h-3">
        <div
          className="h-2 sm:h-3 rounded-full transition-all duration-500"
          style={{
            width: `${Math.min(percentage, 100)}%`,
            backgroundColor: isWarning ? '#ef4444' : color,
          }}
        />
      </div>
      {threshold && (
        <div className="flex justify-between mt-1 text-[10px] sm:text-xs text-gray-500">
          <span>0</span>
          <span className="text-red-500">Threshold: {threshold}</span>
          <span>{max}</span>
        </div>
      )}
      {isWarning && (
        <div className="mt-1 sm:mt-2 text-[10px] sm:text-xs text-red-600 font-medium">
          ⚠️ Below threshold!
        </div>
      )}
    </div>
  );
};

export default SensorGauge;