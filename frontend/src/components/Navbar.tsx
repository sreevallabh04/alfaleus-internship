import { Link } from "react-router-dom"
import { LineChart } from "lucide-react"

const Navbar = () => {
  return (
    <nav className="bg-white shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <LineChart className="h-6 w-6 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">PricePulse</span>
          </Link>
          <div className="flex items-center space-x-4">
            <Link to="/" className="text-gray-700 hover:text-blue-600 transition-colors">
              Home
            </Link>
            <a
              href="https://github.com/yourusername/pricepulse"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-700 hover:text-blue-600 transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
