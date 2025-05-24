"use client"

import type React from "react"

import { Link } from "react-router-dom"
import { ArrowRight, Trash2 } from "lucide-react"
import type { Product } from "../types"
import { formatCurrency } from "../utils/formatters"
import { deleteProduct } from "../services/api"
import toast from "react-hot-toast"

interface ProductCardProps {
  product: Product
  onDelete: () => void
}

const ProductCard = ({ product, onDelete }: ProductCardProps) => {
  const handleDelete = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    if (window.confirm(`Are you sure you want to delete ${product.name}?`)) {
      try {
        await deleteProduct(product.id)
        toast.success("Product deleted successfully")
        onDelete()
      } catch (error) {
        toast.error("Failed to delete product")
        console.error("Error deleting product:", error)
      }
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      <div className="relative h-48 bg-gray-200">
        {product.image_url ? (
          <img
            src={product.image_url || "/placeholder.svg"}
            alt={product.name}
            className="w-full h-full object-contain p-4"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">No image available</div>
        )}
      </div>

      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-800 line-clamp-2 h-14">{product.name}</h3>

        <div className="mt-2">
          <p className="text-2xl font-bold text-blue-600">{formatCurrency(product.current_price, product.currency)}</p>
          <p className="text-sm text-gray-500">Last updated: {new Date(product.updated_at).toLocaleDateString()}</p>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <Link
            to={`/product/${product.id}`}
            className="flex items-center text-blue-600 hover:text-blue-800 transition-colors"
          >
            View details
            <ArrowRight className="ml-1 h-4 w-4" />
          </Link>

          <button
            onClick={handleDelete}
            className="text-red-500 hover:text-red-700 transition-colors"
            aria-label="Delete product"
          >
            <Trash2 className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default ProductCard
