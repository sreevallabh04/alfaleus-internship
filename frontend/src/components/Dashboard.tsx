"use client"

import { useEffect, useState } from "react"
import { TrendingUp, DollarSign, Bell, Package } from "lucide-react"
import { getAllProducts } from "../services/api"
import type { Product } from "../types"
import { formatCurrency } from "../utils/formatters"
import LoadingSpinner from "./LoadingSpinner"

interface DashboardStats {
  totalProducts: number
  totalValue: number
  avgPrice: number
  priceDrops: number
  currency: string
}

const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentProducts, setRecentProducts] = useState<Product[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await getAllProducts()
        if (response.success && response.products) {
          const products = response.products

          // Calculate stats
          const totalProducts = products.length
          const totalValue = products.reduce((sum: number, product: Product) => sum + (product.current_price || 0), 0)
          const avgPrice = totalProducts > 0 ? totalValue / totalProducts : 0
          const priceDrops = 0 // This would need price history to calculate
          const currency = products.length > 0 ? products[0].currency : "USD"

          setStats({
            totalProducts,
            totalValue,
            avgPrice,
            priceDrops,
            currency,
          })

          // Get recent products (last 5)
          setRecentProducts(products.slice(0, 5))
        }
      } catch (error) {
        console.error("Error fetching dashboard data:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (isLoading) {
    return <LoadingSpinner size="lg" text="Loading dashboard..." />
  }

  if (!stats) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Unable to load dashboard data</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Package className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Products</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalProducts}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <DollarSign className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Value</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.totalValue, stats.currency)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Average Price</p>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.avgPrice, stats.currency)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <Bell className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Alerts</p>
              <p className="text-2xl font-bold text-gray-900">{stats.priceDrops}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Products */}
      {recentProducts.length > 0 && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Recently Added Products</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {recentProducts.map((product) => (
                <div key={product.id} className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <img
                      src={product.image_url || "/placeholder.svg?height=50&width=50"}
                      alt={product.name}
                      className="h-12 w-12 object-cover rounded-md"
                    />
                  </div>
                  <div className="flex-grow">
                    <p className="text-sm font-medium text-gray-900 truncate">{product.name}</p>
                    <p className="text-sm text-gray-500">Added {new Date(product.created_at).toLocaleDateString()}</p>
                  </div>
                  <div className="flex-shrink-0">
                    <p className="text-sm font-bold text-blue-600">
                      {formatCurrency(product.current_price, product.currency)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
