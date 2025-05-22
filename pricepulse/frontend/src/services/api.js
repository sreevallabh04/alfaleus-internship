import axios from 'axios';

// Base URL for API - uses proxy in development, window.location based URL in production
const API_URL = process.env.NODE_ENV === 'production' 
  ? `${window.location.origin}/api` 
  : '/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handler helper
const handleApiError = (error) => {
  console.error('API Error:', error);
  if (error.response) {
    // Server responded with an error status
    return {
      success: false,
      error: error.response.data.error || 'Server error',
      status: error.response.status
    };
  } else if (error.request) {
    // Request was made but no response received
    return {
      success: false,
      error: 'No response from server. Please check if the backend is running.',
      serverDown: true
    };
  } else {
    // Something else caused the error
    return {
      success: false,
      error: error.message || 'An unknown error occurred',
    };
  }
};

/**
 * Check if the backend API is running
 */
export const checkApiHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    return {
      success: true,
      message: response.data.message || 'API is running',
      status: response.data.status
    };
  } catch (error) {
    return {
      success: false,
      error: 'Backend server is not running or cannot be reached',
      serverDown: true
    };
  }
};

// Helper function for retrying API calls
const retryApiCall = async (apiCallFn, maxRetries = 2, delayMs = 1000) => {
  let lastError;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await apiCallFn();
    } catch (error) {
      lastError = error;
      if (attempt < maxRetries) {
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
  }
  
  // If we get here, all attempts failed
  return handleApiError(lastError);
};

// Products API

/**
 * Fetch all tracked products
 */
export const getAllProducts = async () => {
  try {
    const response = await apiClient.get('/products');
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetch a specific product by ID
 */
export const getProduct = async (productId) => {
  try {
    const response = await apiClient.get(`/products/${productId}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Add a new product to track
 */
export const addProduct = async (productUrl) => {
  try {
    const response = await apiClient.post('/products', { url: productUrl });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Delete a product from tracking
 */
export const deleteProduct = async (productId) => {
  try {
    const response = await apiClient.delete(`/products/${productId}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Get price history for a product
 */
export const getPriceHistory = async (productId) => {
  try {
    const response = await apiClient.get(`/products/${productId}/prices`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

// Price alerts API

/**
 * Create a price alert for a product
 */
export const createPriceAlert = async (productId, email, targetPrice) => {
  try {
    const response = await apiClient.post('/alerts', {
      product_id: productId,
      email,
      target_price: targetPrice
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Test a product URL without adding it to the database
 */
export const testProductUrl = async (url) => {
  try {
    const response = await apiClient.post('/test-scraper', { url });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export default {
  getAllProducts,
  getProduct,
  addProduct,
  deleteProduct,
  getPriceHistory,
  createPriceAlert,
  testProductUrl
};