import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ChartComponentProps {
  readings: {
    recorded_at: string;
    soil_moisture: number;
    temperature: number;
    humidity: number;
  }[];
  title?: string;
}

const ChartComponent: React.FC<ChartComponentProps> = ({ readings, title = 'Sensor History' }) => {
  // Format time in Uganda local time (UTC+3) with AM/PM
  const formatLocalTime = (dateString: string) => {
    const date = new Date(dateString);
    // Add 3 hours for Uganda time (UTC+3)
    date.setHours(date.getHours() + 3);
    return date.toLocaleString('en-UG', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  const data = {
    labels: readings.map(r => formatLocalTime(r.recorded_at)),
    datasets: [
      {
        label: 'Soil Moisture (%)',
        data: readings.map(r => r.soil_moisture),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 2,
        pointHoverRadius: 6,
      },
      {
        label: 'Temperature (°C)',
        data: readings.map(r => r.temperature),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 2,
        pointHoverRadius: 6,
      },
      {
        label: 'Humidity (%)',
        data: readings.map(r => r.humidity),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 2,
        pointHoverRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 10,
          font: {
            size: 10,
          },
        },
      },
      title: {
        display: true,
        text: title,
        font: {
          size: 14,
          weight: 'bold' as const,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          font: {
            size: 10,
          },
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          maxRotation: 45,
          minRotation: 30,
          font: {
            size: 8,
          },
          maxTicksLimit: 10,
        },
      },
    },
    interaction: {
      intersect: false,
      mode: 'index' as const,
    },
  };

  return (
    <div className="w-full">
      <div className="h-48 xs:h-56 sm:h-64 md:h-72 lg:h-80">
        <Line data={data} options={options} />
      </div>
    </div>
  );
};

export default ChartComponent;