"use client"

import { useEffect, useState } from "react"
import ProductForm from "../components/ProductForm"
import ProductCard from "../components/ProductCard"
import Dashboard from "../components/Dashboard"
import LoadingSpinner from "../components/LoadingSpinner"
import ErrorBanner from "../components/ErrorBanner"
import { getAllProducts } from "../services/api"
import type { Product } from "../types"
import { useLocalStorage } from "../hooks/useLocalStorage"

const HomePage = () => {
  const [products, setProducts] = useState<Product[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [cachedProducts, setCachedProducts] = useLocalStorage<Product[]>("pricepulse_products", [])
  const [activeTab, setActiveTab] = useState<"dashboard" | "products">("dashboard")

  const fetchProducts = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const data = await getAllProducts()
      if (data.success) {
        setProducts(data.products)
        setCachedProducts(data.products)
      } else {
        throw new Error(data.message || "Failed to fetch products")
      }
    } catch (error) {
      console.error("Error fetching products:", error)
      setError("Failed to load products. Please try again.")

      // Use cached products if available
      if (cachedProducts.length > 0) {
        setProducts(cachedProducts)
      }
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchProducts()
  }, [])

  const handleProductAdded = () => {
    fetchProducts()
  }

  const handleProductDeleted = () => {
    fetchProducts()
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <section className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to <span className="text-blue-600">PricePulse</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8">Track product prices, get alerts, and never miss a deal again</p>
      </section>

      {/* Product Form */}
      <section>
        <ProductForm onProductAdded={handleProductAdded} />
      </section>

      {/* Tab Navigation */}
      <section>
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === "dashboard"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab("products")}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === "products"
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              All Products ({products.length})
            </button>
          </nav>
        </div>
      </section>

      {/* Tab Content */}
      <section>
        {activeTab === "dashboard" && <Dashboard />}

        {activeTab === "products" && (
          <div>
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">Your Tracked Products</h2>

            {isLoading ? (
              <LoadingSpinner size="lg" text="Loading products..." />
            ) : error ? (
              <ErrorBanner message={error} onRetry={fetchProducts} />
            ) : products.length === 0 ? (
              <div className="bg-white p-8 rounded-lg shadow-md text-center">
                <div className="max-w-md mx-auto">
                  <div className="mb-4">
                    <svg
                      className="mx-auto h-12 w-12 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2 2v-5m16 0h-2M4 13h2m13-8V4a1 1 0 00-1-1H7a1 1 0 00-1 1v1m8 0V4a1 1 0 00-1-1H9a1 1 0 00-1 1v1"
                      />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No products tracked yet</h3>
                  <p className="text-gray-500 mb-4">
                    Start tracking your favorite products by adding their URLs above.
                  </p>
                  <p className="text-sm text-gray-400">
                    We'll monitor price changes and send you alerts when prices drop!
                  </p>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map((product) => (
                  <ProductCard key={product.id} product={product} onDelete={handleProductDeleted} />
                ))}
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  )
}

export default HomePage
