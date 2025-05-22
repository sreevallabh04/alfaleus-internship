import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import moment from 'moment';
import 'chartjs-adapter-moment';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const PriceChart = ({ priceHistory, title = 'Price History' }) => {
  // Return placeholder if no data
  if (!priceHistory || priceHistory.length === 0) {
    return (
      <div className="price-graph p-4 text-center">
        <p className="text-muted">No price history available yet. Check back later.</p>
      </div>
    );
  }

  // Sort price history by timestamp
  const sortedPriceHistory = [...priceHistory].sort(
    (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
  );

  // Prepare data for chart
  const chartData = {
    labels: sortedPriceHistory.map(record => moment(record.timestamp)),
    datasets: [
      {
        label: 'Price',
        data: sortedPriceHistory.map(record => record.price),
        fill: false,
        backgroundColor: 'rgba(76, 175, 80, 0.2)',
        borderColor: '#4CAF50',
        tension: 0.1,
        pointBackgroundColor: '#4CAF50',
        pointBorderColor: '#fff',
        pointRadius: 5,
        pointHoverRadius: 7,
      },
    ],
  };

  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: title,
        font: {
          size: 16,
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `Price: ₹${context.parsed.y.toFixed(2)}`;
          },
          title: (tooltipItems) => {
            return moment(tooltipItems[0].parsed.x).format('MMM D, YYYY [at] h:mm A');
          }
        }
      }
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'day',
          tooltipFormat: 'MMM D, YYYY',
          displayFormats: {
            day: 'MMM D'
          }
        },
        title: {
          display: true,
          text: 'Date'
        }
      },
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: 'Price (₹)'
        },
        ticks: {
          callback: (value) => {
            return '₹' + value;
          }
        }
      }
    }
  };

  // Calculate price statistics
  const currentPrice = sortedPriceHistory[sortedPriceHistory.length - 1].price;
  const lowestPrice = Math.min(...sortedPriceHistory.map(record => record.price));
  const highestPrice = Math.max(...sortedPriceHistory.map(record => record.price));
  const averagePrice = sortedPriceHistory.reduce((sum, record) => sum + record.price, 0) / sortedPriceHistory.length;

  return (
    <div className="price-graph">
      <div className="chart-container mb-3">
        <Line data={chartData} options={options} />
      </div>
      
      <div className="row row-cols-2 row-cols-md-4 g-3 text-center">
        <div className="col">
          <div className="card h-100">
            <div className="card-body">
              <h6 className="card-subtitle mb-1 text-muted">Current</h6>
              <p className="card-text fs-4 fw-bold text-success">₹{currentPrice.toFixed(2)}</p>
            </div>
          </div>
        </div>
        
        <div className="col">
          <div className="card h-100">
            <div className="card-body">
              <h6 className="card-subtitle mb-1 text-muted">Lowest</h6>
              <p className="card-text fs-4 fw-bold text-primary">₹{lowestPrice.toFixed(2)}</p>
            </div>
          </div>
        </div>
        
        <div className="col">
          <div className="card h-100">
            <div className="card-body">
              <h6 className="card-subtitle mb-1 text-muted">Highest</h6>
              <p className="card-text fs-4 fw-bold text-danger">₹{highestPrice.toFixed(2)}</p>
            </div>
          </div>
        </div>
        
        <div className="col">
          <div className="card h-100">
            <div className="card-body">
              <h6 className="card-subtitle mb-1 text-muted">Average</h6>
              <p className="card-text fs-4 fw-bold text-secondary">₹{averagePrice.toFixed(2)}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PriceChart;