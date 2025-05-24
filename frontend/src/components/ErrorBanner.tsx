"use client"

import { AlertTriangle } from "lucide-react"

interface ErrorBannerProps {
  message: string
  onRetry?: () => void
}

const ErrorBanner = ({ message, onRetry }: ErrorBannerProps) => {
  return (
    <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <AlertTriangle className="h-5 w-5 text-red-500" />
        </div>
        <div className="ml-3">
          <p className="text-sm text-red-700">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-2 text-sm font-medium text-red-700 hover:text-red-600 focus:outline-none"
            >
              Try again
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default ErrorBanner
