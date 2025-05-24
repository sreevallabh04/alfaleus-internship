"use client"

import type React from "react"

import { useState } from "react"
import { Bell } from "lucide-react"
import { createAlert } from "../services/api"
import toast from "react-hot-toast"
import type { Product } from "../types"
import { formatCurrency } from "../utils/formatters"

interface PriceAlertFormProps {
  product: Product
}

const PriceAlertForm = ({ product }: PriceAlertFormProps) => {
  const [email, setEmail] = useState("")
  const [targetPrice, setTargetPrice] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validate form
    if (!email.trim()) {
      toast.error("Please enter your email")
      return
    }

    // Simple email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      toast.error("Please enter a valid email")
      return
    }

    if (!targetPrice.trim()) {
      toast.error("Please enter a target price")
      return
    }

    const price = Number.parseFloat(targetPrice)
    if (isNaN(price) || price <= 0) {
      toast.error("Please enter a valid price")
      return
    }

    setIsLoading(true)

    try {
      const response = await createAlert({
        product_id: product.id,
        email,
        target_price: price,
      })

      if (response.success) {
        toast.success("Price alert created successfully")
        setEmail("")
        setTargetPrice("")
      } else {
        toast.error(response.message || "Failed to create price alert")
      }
    } catch (error) {
      toast.error("Failed to create price alert. Please try again.")
      console.error("Error creating price alert:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
        <Bell className="mr-2 h-5 w-5 text-blue-600" />
        Set Price Alert
      </h3>

      <p className="text-sm text-gray-600 mb-4">Get notified when the price drops below your target price.</p>

      <form onSubmit={handleSubmit}>
        <div className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="targetPrice" className="block text-sm font-medium text-gray-700 mb-1">
              Target Price ({product.currency})
            </label>
            <input
              id="targetPrice"
              type="number"
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              placeholder={`Current: ${product.current_price}`}
              step="0.01"
              min="0.01"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <p className="mt-1 text-xs text-gray-500">
              Current price: {formatCurrency(product.current_price, product.currency)}
            </p>
          </div>

          <button
            type="submit"
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            disabled={isLoading}
          >
            {isLoading ? "Creating Alert..." : "Create Alert"}
          </button>
        </div>
      </form>
    </div>
  )
}

export default PriceAlertForm
