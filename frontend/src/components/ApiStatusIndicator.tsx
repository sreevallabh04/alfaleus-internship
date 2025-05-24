"use client"

import { useEffect, useState } from "react"
import { checkApiHealth } from "../services/api"
import { Wifi, WifiOff } from "lucide-react"

const ApiStatusIndicator = () => {
  const [isConnected, setIsConnected] = useState<boolean | null>(null)

  useEffect(() => {
    const checkConnection = async () => {
      try {
        await checkApiHealth()
        setIsConnected(true)
      } catch (error) {
        setIsConnected(false)
      }
    }

    // Check connection on mount
    checkConnection()

    // Set up interval to check connection periodically
    const interval = setInterval(checkConnection, 30000) // Check every 30 seconds

    return () => clearInterval(interval)
  }, [])

  if (isConnected === null) {
    return null // Don't show anything while initial check is in progress
  }

  return (
    <div className="fixed bottom-4 left-4 z-50">
      <div
        className={`flex items-center space-x-2 px-3 py-2 rounded-full shadow-md ${
          isConnected ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
        }`}
      >
        {isConnected ? (
          <>
            <Wifi className="h-4 w-4" />
            <span className="text-xs font-medium">Connected to Server</span>
          </>
        ) : (
          <>
            <WifiOff className="h-4 w-4" />
            <span className="text-xs font-medium">Server Disconnected</span>
          </>
        )}
      </div>
    </div>
  )
}

export default ApiStatusIndicator
