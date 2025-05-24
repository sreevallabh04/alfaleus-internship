"use client"

import type React from "react"

import { useState } from "react"
import { Search } from "lucide-react"
import { addProduct } from "../services/api"
import toast from "react-hot-toast"

interface ProductFormProps {
  onProductAdded: () => void
}

const ProductForm = ({ onProductAdded }: ProductFormProps) => {
  const [url, setUrl] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validate URL
    if (!url.trim()) {
      toast.error("Please enter a product URL")
      return
    }

    // Simple URL validation
    try {
      new URL(url)
    } catch (error) {
      toast.error("Please enter a valid URL")
      return
    }

    setIsLoading(true)

    try {
      const loadingToast = toast.loading("Tracking product...")

      const response = await addProduct(url)

      toast.dismiss(loadingToast)

      if (response.success) {
        toast.success(response.message || "Product added successfully")
        setUrl("")
        onProductAdded()
      } else {
        toast.error(response.message || "Failed to add product")
      }
    } catch (error) {
      toast.error("Failed to add product. Please try again.")
      console.error("Error adding product:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Track a New Product</h2>

      <form onSubmit={handleSubmit}>
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-grow">
            <label htmlFor="productUrl" className="sr-only">
              Product URL
            </label>
            <input
              id="productUrl"
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Paste Amazon product URL here"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
          </div>

          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors flex items-center justify-center"
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
                Processing
              </span>
            ) : (
              <span className="flex items-center">
                <Search className="mr-2 h-4 w-4" />
                Track Product
              </span>
            )}
          </button>
        </div>

        <p className="mt-2 text-sm text-gray-500">Currently supports Amazon products. Paste the full product URL.</p>
      </form>
    </div>
  )
}

export default ProductForm
