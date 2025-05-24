"use client"

import { useEffect, useState } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"
import type { PriceRecord } from "../types"
import { formatCurrency } from "../utils/formatters"

interface PriceChartProps {
  priceHistory: PriceRecord[]
  currency: string
}

interface ChartData {
  date: string
  price: number
}

const PriceChart = ({ priceHistory, currency }: PriceChartProps) => {
  const [chartData, setChartData] = useState<ChartData[]>([])

  useEffect(() => {
    // Transform price history data for the chart
    const formattedData = priceHistory.map((record) => ({
      date: new Date(record.timestamp).toLocaleDateString(),
      price: record.price,
    }))

    setChartData(formattedData)
  }, [priceHistory])

  // If no price history, show a message
  if (priceHistory.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md text-center">
        <p className="text-gray-500">No price history available yet.</p>
        <p className="text-sm text-gray-400 mt-2">Price history will be updated automatically every hour.</p>
      </div>
    )
  }

  // Calculate min and max prices for Y-axis domain
  const prices = priceHistory.map((record) => record.price)
  const minPrice = Math.min(...prices) * 0.95 // 5% below minimum
  const maxPrice = Math.max(...prices) * 1.05 // 5% above maximum

  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Price History</h3>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} tickMargin={10} />
            <YAxis
              domain={[minPrice, maxPrice]}
              tickFormatter={(value) => formatCurrency(value, currency, false)}
              tick={{ fontSize: 12 }}
              width={80}
            />
            <Tooltip
              formatter={(value) => [formatCurrency(value as number, currency), "Price"]}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name="Price"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default PriceChart
