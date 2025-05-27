import axios from "axios";
import toast from "react-hot-toast";
import { ProductData, PriceHistory, ApiResponse } from '../types';

// Determine the API base URL based on environment
const getBaseUrl = () => {
  // Use environment variable if available
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // In production on Vercel, use the same domain with /api prefix
  if (import.meta.env.PROD && window.location.hostname.includes("vercel.app")) {
    return `${window.location.origin}/api`;
  }

  // Default for local development
  return "http://localhost:5000/api";
};

// Create axios instance with base URL
const api = axios.create({
  baseURL: getBaseUrl(),
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor for authentication if needed
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if implementing authentication
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle network errors
    if (!error.response) {
      toast.error("Network error. Please check your internet connection.");
      return Promise.reject({
        success: false,
        message: "Network error. Please check your internet connection.",
      });
    }

    // Handle API errors
    const errorMessage = error.response.data?.message || "An unexpected error occurred";

    // Don't show toast for health check errors to avoid spamming the user
    if (!error.config.url.includes("/health")) {
      toast.error(errorMessage);
    }

    return Promise.reject(
      error.response.data || {
        success: false,
        message: errorMessage,
      }
    );
  }
);

// Health check
export const checkApiHealth = async () => {
  try {
    const response = await api.get("/health");
    return response.data;
  } catch (error) {
    console.error("Health check failed:", error);
    throw error;
  }
};

// Get all products
export const getAllProducts = async () => {
  try {
    const response = await api.get("/products");
    return response.data;
  } catch (error) {
    console.error("Error fetching products:", error);
    // Return empty products array as fallback
    return { success: false, products: [] };
  }
};

// Alias for backwards compatibility
export const getProducts = getAllProducts;

// Get a specific product
export const getProduct = async (id: number): Promise<ApiResponse> => {
  const response = await api.get(`/products/${id}`);
  return response.data;
};

// Get price history for a product
export const getPriceHistory = async (id: number): Promise<PriceHistory[]> => {
  const response = await api.get(`/products/${id}/history`);
  return response.data;
};

// Add a new product
export const addProduct = async (
  amazonUrl: string,
  targetPrice: number,
  email: string
): Promise<ApiResponse> => {
  const response = await api.post('/products', {
    amazon_url: amazonUrl,
    target_price: targetPrice,
    email,
  });
  return response.data;
};

// Delete a product
export const deleteProduct = async (id: number): Promise<void> => {
  await api.delete(`/products/${id}`);
};

// Create a price alert
export const createAlert = async (alertData: {
  product_id: number;
  email: string;
  target_price: number;
}) => {
  const response = await api.post("/alerts", alertData);
  return response.data;
};

// Delete a price alert
export const deleteAlert = async (id: number) => {
  const response = await api.delete(`/alerts/${id}`);
  return response.data;
};

// Compare product across platforms
export const compareProducts = async (url: string) => {
  const response = await api.post("/compare", { url });
  return response.data;
};

export default api;
