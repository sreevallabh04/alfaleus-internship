"use client"

import { useEffect, useState } from "react"
import { TrendingUp, DollarSign, Bell, Package, Sparkles, ArrowRight } from "lucide-react"
import { getAllProducts } from "../services/api"
import type { Product } from "../types"
import { formatCurrency } from "../utils/formatters"
import LoadingSpinner from "./LoadingSpinner"
import { Link } from "react-router-dom"

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
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading dashboard data..." />
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="text-center py-12 card">
        <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-lg font-medium text-gray-500">No dashboard data available</p>
        <p className="text-sm text-gray-400 mt-2">Add some products to get started</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="card-gradient gradient-primary mb-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">Welcome to PricePulse</h2>
            <p className="text-blue-100 mb-4">Monitor product prices across multiple platforms in one place</p>
          </div>
          <div className="mt-4 md:mt-0">
            <button className="bg-white text-blue-600 hover:bg-blue-50 px-4 py-2 rounded-lg shadow-md transition-all hover:-translate-y-1 hover:shadow-lg font-medium flex items-center">
              Add New Product
              <ArrowRight className="ml-2 h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="stat-card group">
          <div className="absolute inset-0 bg-blue-500 opacity-0 rounded-xl group-hover:opacity-5 transition-opacity duration-300"></div>
          <div className="flex items-center">
            <div className="p-3 gradient-primary rounded-xl shadow-md">
              <Package className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Products</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.totalProducts}</p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="absolute inset-0 bg-green-500 opacity-0 rounded-xl group-hover:opacity-5 transition-opacity duration-300"></div>
          <div className="flex items-center">
            <div className="p-3 gradient-success rounded-xl shadow-md">
              <DollarSign className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Value</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatCurrency(stats.totalValue, stats.currency)}</p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="absolute inset-0 bg-purple-500 opacity-0 rounded-xl group-hover:opacity-5 transition-opacity duration-300"></div>
          <div className="flex items-center">
            <div className="p-3 gradient-purple rounded-xl shadow-md">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Average Price</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatCurrency(stats.avgPrice, stats.currency)}</p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="absolute inset-0 bg-red-500 opacity-0 rounded-xl group-hover:opacity-5 transition-opacity duration-300"></div>
          <div className="flex items-center">
            <div className="p-3 gradient-danger rounded-xl shadow-md">
              <Bell className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Active Alerts</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.priceDrops}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Products */}
      {recentProducts.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">Recently Added Products</h3>
            <Link 
              to="/products"
              className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 text-sm font-medium flex items-center transition-colors"
            >
              View All
              <ArrowRight className="ml-1 h-4 w-4" />
            </Link>
          </div>
          
          <div className="space-y-5">
            {recentProducts.map((product) => (
              <Link to={`/product/${product.id}`} key={product.id} className="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                <div className="flex-shrink-0 bg-gray-100 dark:bg-gray-700 rounded-lg p-1 shadow-sm">
                  <img
                    src={product.image_url || "/placeholder.svg?height=50&width=50"}
                    alt={product.name}
                    className="h-14 w-14 object-contain rounded-md"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = "/placeholder.svg?height=50&width=50";
                    }}
                  />
                </div>
                <div className="flex-grow min-w-0">
                  <p className="font-medium text-gray-900 dark:text-white truncate">{product.name}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Added {new Date(product.created_at).toLocaleDateString()}</p>
                </div>
                <div className="flex-shrink-0">
                  <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
                    {formatCurrency(product.current_price, product.currency)}
                  </p>
                </div>
              </Link>
            ))}
          </div>
          
          {recentProducts.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-100 dark:border-gray-700 text-center">
              <button className="btn btn-secondary w-full">
                Add New Product
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Dashboard
