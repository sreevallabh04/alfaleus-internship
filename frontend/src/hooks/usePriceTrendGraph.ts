import { useMemo } from 'react';
import { PriceHistory } from '../types';
import { formatPrice } from '../utils/helpers';

interface UsePriceTrendGraphProps {
  priceHistory: PriceHistory[];
  currentPrice: number;
  targetPrice: number;
}

export const usePriceTrendGraph = ({
  priceHistory,
  currentPrice,
  targetPrice
}: UsePriceTrendGraphProps) => {
  const chartData = useMemo(() => {
    const labels = priceHistory.map(history => {
      const date = new Date(history.timestamp);
      return date.toLocaleDateString();
    });

    const prices = priceHistory.map(history => history.price);
    const targetPrices = Array(priceHistory.length).fill(targetPrice);

    return {
      labels,
      datasets: [
        {
          label: 'Price History',
          data: prices,
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Target Price',
          data: targetPrices,
          borderColor: 'rgb(239, 68, 68)',
          borderDash: [5, 5],
          fill: false
        }
      ]
    };
  }, [priceHistory, targetPrice]);

  const options = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: 'rgb(156, 163, 175)'
        }
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            return `${label}: ${formatPrice(value)}`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(156, 163, 175, 0.1)'
        },
        ticks: {
          color: 'rgb(156, 163, 175)'
        }
      },
      y: {
        grid: {
          color: 'rgba(156, 163, 175, 0.1)'
        },
        ticks: {
          color: 'rgb(156, 163, 175)',
          callback: (value: number) => formatPrice(value)
        }
      }
    }
  }), []);

  const currentPriceData = useMemo(() => ({
    labels: ['Current Price'],
    datasets: [
      {
        data: [currentPrice],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1
      }
    ]
  }), [currentPrice]);

  const currentPriceOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const value = context.parsed.y;
            return formatPrice(value);
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          display: false
        },
        ticks: {
          display: false
        }
      },
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: 'rgb(156, 163, 175)'
        }
      }
    }
  }), []);

  return {
    chartData,
    options,
    currentPriceData,
    currentPriceOptions
  };
}; 