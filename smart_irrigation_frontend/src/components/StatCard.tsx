import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  color: 'green' | 'red' | 'blue' | 'gray' | 'yellow';
}

const StatCard: React.FC<StatCardProps> = ({ title, value, change, color }) => {
  const colorClasses = {
    green: 'bg-green-100 text-green-800 border-green-200',
    red: 'bg-red-100 text-red-800 border-red-200',
    blue: 'bg-blue-100 text-blue-800 border-blue-200',
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    gray: 'bg-gray-100 text-gray-800 border-gray-200',
  };

  return (
    <div className={`p-3 sm:p-4 rounded-lg border ${colorClasses[color]} shadow-sm`}>
      <h3 className="text-xs sm:text-sm font-medium opacity-80">{title}</h3>
      <p className="text-lg sm:text-2xl font-bold mt-0.5 sm:mt-1">{value}</p>
      {change && <p className="text-[10px] sm:text-xs opacity-70 mt-0.5 sm:mt-1">{change}</p>}
    </div>
  );
};

export default StatCard;