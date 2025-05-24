"use client"

import type React from "react"

import { useState } from "react"
import { Search } from "lucide-react"
import { compareProducts } from "../services/api"
import toast from "react-hot-toast"

interface CompareFormProps {
  productUrl: string
}

interface Comparison {
  platform: string
  url: string
  price: number | null
  currency: string
  in_stock: boolean | null
  last_checked: string | null
  is_genuine_match?: boolean
  match_confidence?: number
}

interface CompareResult {
  metadata: {
    name: string
    brand: string
    model?: string
    category?: string
    key_features?: string[]
    price: number
    currency: string
    image_url: string
  }
  comparisons: Comparison[]
}

const CompareForm = ({ productUrl }: CompareFormProps) => {
  const [isLoading, setIsLoading] = useState(false)
  const [compareResult, setCompareResult] = useState<CompareResult | null>(null)

  const handleCompare = async (e: React.MouseEvent) => {
    e.preventDefault()

    if (!productUrl.trim()) {
      toast.error("No product URL to compare")
      return
    }

    setIsLoading(true)

    try {
      const loadingToast = toast.loading("Comparing prices across platforms...")

      const response = await compareProducts(productUrl)

      toast.dismiss(loadingToast)

      if (response.success) {
        setCompareResult(response)
        toast.success("Price comparison complete")
      } else {
        toast.error(response.message || "Failed to compare prices")
      }
    } catch (error) {
      toast.error("Failed to compare prices. Please try again.")
      console.error("Error comparing prices:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
        <Search className="mr-2 h-5 w-5 text-blue-600" />
        Compare Across Platforms
      </h3>

      <p className="text-sm text-gray-600 mb-4">Find and compare this product on other e-commerce platforms.</p>

      <button
        onClick={handleCompare}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors flex items-center justify-center"
        disabled={isLoading}
      >
        {isLoading ? (
          <span className="flex items-center">
            <svg
              className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Comparing...
          </span>
        ) : (
          <span className="flex items-center">
            <Search className="mr-2 h-4 w-4" />
            Compare Prices
          </span>
        )}
      </button>

      {compareResult && (
        <div className="mt-6">
          <h4 className="font-medium text-gray-800 mb-2">Product Information</h4>
          <div className="bg-gray-50 p-3 rounded-md mb-4">
            <p>
              <span className="font-medium">Name:</span> {compareResult.metadata.name}
            </p>
            <p>
              <span className="font-medium">Brand:</span> {compareResult.metadata.brand}
            </p>
            {compareResult.metadata.model && (
              <p>
                <span className="font-medium">Model:</span> {compareResult.metadata.model}
              </p>
            )}
            {compareResult.metadata.category && (
              <p>
                <span className="font-medium">Category:</span> {compareResult.metadata.category}
              </p>
            )}
            {compareResult.metadata.key_features && (
              <div>
                <span className="font-medium">Key Features:</span>
                <ul className="list-disc list-inside ml-2 text-sm">
                  {compareResult.metadata.key_features.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <h4 className="font-medium text-gray-800 mb-2">Price Comparison</h4>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Platform
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Link
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {/* Filter to only show genuine matches (or all if none are marked as genuine) */}
                {compareResult.comparisons
                  .filter(comparison => {
                    // If no comparisons have the is_genuine_match flag, show all
                    const hasGenuineFlag = compareResult.comparisons.some(c => c.is_genuine_match !== undefined);
                    return hasGenuineFlag ? comparison.is_genuine_match === true : true;
                  })
                  .map((comparison, index) => (
                    <tr key={index} className={comparison.match_confidence && comparison.match_confidence > 0.8 ? 'bg-green-50' : ''}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        <div className="flex items-center">
                          {comparison.match_confidence && comparison.match_confidence > 0.8 && (
                            <span className="inline-flex mr-2 items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700">
                              Exact Match
                            </span>
                          )}
                          {comparison.platform}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {comparison.price ? `${comparison.currency} ${comparison.price}` : "Not available"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600">
                        <a href={comparison.url} target="_blank" rel="noopener noreferrer">
                          View
                        </a>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Note: Only showing exact matches for the same product. We identify the exact same products using keywords from the 
            product title and important specifications.
          </p>
        </div>
      )}
    </div>
  )
}

export default CompareForm
