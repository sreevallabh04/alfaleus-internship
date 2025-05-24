"use client"

import { useEffect, useState } from "react"
import { useParams, Link } from "react-router-dom"
import { ArrowLeft, ExternalLink } from "lucide-react"
import PriceChart from "../components/PriceChart"
import PriceAlertForm from "../components/PriceAlertForm"
import CompareForm from "../components/CompareForm"
import Loader from "../components/Loader"
import ErrorBanner from "../components/ErrorBanner"
import { getProduct } from "../services/api"
import type { Product, PriceRecord } from "../types"
import { formatCurrency } from "../utils/formatters"

const ProductDetailPage = () => {
  const { id } = useParams<{ id: string }>()
  const [product, setProduct] = useState<Product | null>(null)
  const [priceHistory, setPriceHistory] = useState<PriceRecord[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchProductDetails = async () => {
      if (!id) return

      setIsLoading(true)
      setError(null)

      try {
        const data = await getProduct(Number.parseInt(id))
        setProduct(data.product)
        setPriceHistory(data.price_history)
      } catch (error) {
        console.error("Error fetching product details:", error)
        setError("Failed to load product details. Please try again.")
      } finally {
        setIsLoading(false)
      }
    }

    fetchProductDetails()
  }, [id])

  if (isLoading) {
    return <Loader />
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Link to="/" className="inline-flex items-center text-blue-600 hover:text-blue-800">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Home
        </Link>
        <ErrorBanner message={error} />
      </div>
    )
  }

  if (!product) {
    return (
      <div className="space-y-4">
        <Link to="/" className="inline-flex items-center text-blue-600 hover:text-blue-800">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Home
        </Link>
        <div className="bg-white p-6 rounded-lg shadow-md text-center">
          <p className="text-gray-500">Product not found.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Link to="/" className="inline-flex items-center text-blue-600 hover:text-blue-800">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Home
      </Link>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="md:w-1/3 flex justify-center">
              {product.image_url ? (
                <img
                  src={product.image_url || "/placeholder.svg"}
                  alt={product.name}
                  className="max-h-64 object-contain"
                />
              ) : (
                <div className="w-full h-64 bg-gray-200 flex items-center justify-center text-gray-400">
                  No image available
                </div>
              )}
            </div>

            <div className="md:w-2/3">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{product.name}</h1>

              <div className="flex items-center mb-4">
                <a
                  href={product.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 flex items-center text-sm"
                >
                  View on Amazon
                  <ExternalLink className="ml-1 h-3 w-3" />
                </a>
              </div>

              <div className="mb-4">
                <p className="text-3xl font-bold text-blue-600">
                  {formatCurrency(product.current_price, product.currency)}
                </p>
                <p className="text-sm text-gray-500">Last updated: {new Date(product.updated_at).toLocaleString()}</p>
              </div>

              {product.description && (
                <div className="mb-4">
                  <h2 className="text-lg font-semibold text-gray-800 mb-2">Description</h2>
                  <p className="text-gray-600 text-sm">
                    {product.description.length > 300
                      ? `${product.description.substring(0, 300)}...`
                      : product.description}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <PriceChart priceHistory={priceHistory} currency={product.currency} />
        </div>

        <div className="space-y-6">
          <PriceAlertForm product={product} />
          <CompareForm productUrl={product.url} />
        </div>
      </div>
    </div>
  )
}

export default ProductDetailPage
