import React from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { usePriceTrendGraph } from '../hooks/usePriceTrendGraph';
import { PriceHistory } from '../types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface PriceTrendGraphProps {
  priceHistory: PriceHistory[];
  currentPrice: number;
  targetPrice: number;
}

const PriceTrendGraph: React.FC<PriceTrendGraphProps> = ({
  priceHistory,
  currentPrice,
  targetPrice
}) => {
  const { chartData, options, currentPriceData, currentPriceOptions } = usePriceTrendGraph({
    priceHistory,
    currentPrice,
    targetPrice
  });

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Price History
      </h3>
      <div className="h-64 mb-4">
        <Line data={chartData} options={options} />
      </div>
      <div className="h-16">
        <Bar data={currentPriceData} options={currentPriceOptions} />
      </div>
    </div>
  );
};

export default PriceTrendGraph; 