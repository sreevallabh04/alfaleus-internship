"use client"

import type React from "react"

import { Link } from "react-router-dom"
import { ArrowRight, Trash2, PieChart, Tag } from "lucide-react"
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

  // Determine if there was a price drop (would need historical data)
  const hasPriceDrop = false;
  
  return (
    <div className="card group overflow-hidden hover:-translate-y-1 transition-all duration-300">
      {/* Price badge */}
      <div className="absolute top-3 right-3 z-10">
        <div className={`${hasPriceDrop ? "gradient-danger" : "gradient-primary"} text-white px-3 py-1 rounded-full text-sm font-bold shadow-md flex items-center`}>
          <Tag className="h-3 w-3 mr-1" />
          {formatCurrency(product.current_price, product.currency)}
        </div>
      </div>
      
      {/* Image section with gradient overlay */}
      <div className="relative h-48 bg-gray-50 dark:bg-gray-800 rounded-t-xl overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-gray-900/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        {product.image_url ? (
          <img
            src={product.image_url || "/placeholder.svg"}
            alt={product.name}
            className="w-full h-full object-contain p-4"
            onError={(e) => {
              (e.target as HTMLImageElement).src = "/placeholder.svg";
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <PieChart className="h-12 w-12 opacity-30" />
          </div>
        )}
      </div>

      <div className="p-5">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white line-clamp-2 h-14 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
          {product.name}
        </h3>

        <div className="mt-3 flex items-center text-sm text-gray-500 dark:text-gray-400">
          <span className="flex-shrink-0">Last updated:</span>
          <span className="ml-1 text-gray-700 dark:text-gray-300">{new Date(product.updated_at).toLocaleDateString()}</span>
        </div>

        <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 flex items-center justify-between">
          <Link
            to={`/product/${product.id}`}
            className="btn btn-primary text-sm py-1.5"
          >
            View details
            <ArrowRight className="ml-1 h-4 w-4" />
          </Link>

          <button
            onClick={handleDelete}
            className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition-colors"
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
