"use client"

import { useEffect, useState } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"
import type { PriceRecord } from "../types"
import { formatCurrency } from "../utils/formatters"

// Assuming priceHistory is now grouped by platform
interface PriceChartProps {
  priceHistory: { [platform: string]: PriceRecord[] };
  currency: string; // Currency might vary, but using a single one for formatter for now
}

interface ChartData {
  date: string;
  [platform: string]: number | undefined; // Price for each platform on this date
}

const getPlatformColor = (platform: string): string => {
  switch (platform.toLowerCase()) {
    case 'amazon':
      return '#FF9900'; // Amazon orange
    case 'flipkart':
      return '#2874F0'; // Flipkart blue
    case 'meesho':
      return '#F43397'; // Meesho pink
    case 'bigbasket':
      return '#84CC16'; // BigBasket green
    case 'swiggy instamart':
      return '#FC8019'; // Swiggy orange
    case 'snapdeal':
      return '#E40046'; // Snapdeal red
    case 'reliance digital':
      return '#0033A0'; // Reliance Digital blue
    case 'tata cliq':
      return '#6F2DA8'; // Tata Cliq purple
    case 'croma':
      return '#000000'; // Croma black
    default:
      return '#8884d8'; // Default color
  }
};


const PriceChart = ({ priceHistory, currency }: PriceChartProps) => {
  const [chartData, setChartData] = useState<ChartData[]>([])
  const [platforms, setPlatforms] = useState<string[]>([]);


  useEffect(() => {
    const allDates = new Set<string>();
    const dataByDate: { [date: string]: { [platform: string]: number } } = {};
    const availablePlatforms: string[] = [];

    // Collect all unique dates and prices by date and platform
    Object.keys(priceHistory).forEach(platform => {
      availablePlatforms.push(platform);
      priceHistory[platform].forEach(record => {
        const date = new Date(record.timestamp).toLocaleDateString();
        allDates.add(date);
        if (!dataByDate[date]) {
          dataByDate[date] = {};
        }
        dataByDate[date][platform] = record.price;
      });
    });

    setPlatforms(availablePlatforms);

    // Sort dates chronologically
    const sortedDates = Array.from(allDates).sort((a, b) => new Date(a).getTime() - new Date(b).getTime());

    // Create the final chart data array, filling in missing dates with previous values
    const formattedData: ChartData[] = [];
    const lastPrices: { [platform: string]: number | undefined } = {};

    sortedDates.forEach(date => {
        const entry: ChartData = { date };
        availablePlatforms.forEach(platform => {
            // Use the price from dataByDate if available for this date and platform
            if (dataByDate[date] && dataByDate[date][platform] !== undefined) {
                entry[platform] = dataByDate[date][platform];
                lastPrices[platform] = entry[platform]; // Update last known price
            } else {
                // If no price for this date, use the last known price
                entry[platform] = lastPrices[platform];
            }
        });
        formattedData.push(entry);
    });


    setChartData(formattedData);
  }, [priceHistory]); // Dependency on priceHistory

  // If no price history across all platforms, show a message
  const totalRecords = Object.values(priceHistory).reduce((sum, records) => sum + records.length, 0);

  if (totalRecords === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md text-center">
        <p className="text-gray-500">No price history available yet for any platform.</p>
        <p className="text-sm text-gray-400 mt-2">Price history will be updated automatically.</p>
      </div>
    )
  }

  // Calculate min and max prices across all platforms for Y-axis domain
  const allPrices = Object.values(priceHistory).flatMap(records => records.map(record => record.price));
  const minPrice = Math.min(...allPrices) * 0.95 // 5% below minimum
  const maxPrice = Math.max(...allPrices) * 1.05 // 5% above maximum

  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Price History Across Platforms</h3>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} tickMargin={10} />
            <YAxis
              domain={[minPrice, maxPrice]}
              tickFormatter={(value) => formatCurrency(value as number, currency, false)}
              tick={{ fontSize: 12 }}
              width={80}
            />
            <Tooltip
              formatter={(value, name) => [formatCurrency(value as number, currency), name]} // Show value and platform name
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Legend />
            {platforms.map(platform => (
              <Line
                key={platform}
                type="monotone"
                dataKey={platform} // Use platform name as data key
                stroke={getPlatformColor(platform)}
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
                name={platform} // Use platform name for legend
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default PriceChart
