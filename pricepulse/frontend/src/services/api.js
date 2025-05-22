import axios from 'axios';

// Offline mode management
const OFFLINE_MODE_KEY = 'pricepulse_offline_mode';
const CACHED_DATA_KEY = 'pricepulse_cached_data';

// Flag to enable offline mode when backend is unavailable
export const isOfflineMode = () => {
  return localStorage.getItem(OFFLINE_MODE_KEY) === 'true';
};

export const setOfflineMode = (enabled) => {
  localStorage.setItem(OFFLINE_MODE_KEY, enabled ? 'true' : 'false');
  // Dispatch an event so components can react to offline mode changes
  window.dispatchEvent(new CustomEvent('offlinemodechange', { detail: { enabled } }));
};

// Cache management functions
const getCachedData = (key) => {
  try {
    const cachedData = localStorage.getItem(CACHED_DATA_KEY);
    if (!cachedData) return null;
    
    const parsedCache = JSON.parse(cachedData);
    return parsedCache[key] || null;
  } catch (e) {
    console.error('Error reading cache:', e);
    return null;
  }
};

const setCachedData = (key, data) => {
  try {
    const existingCache = localStorage.getItem(CACHED_DATA_KEY);
    const cache = existingCache ? JSON.parse(existingCache) : {};
    
    cache[key] = {
      data,
      timestamp: new Date().toISOString()
    };
    
    localStorage.setItem(CACHED_DATA_KEY, JSON.stringify(cache));
  } catch (e) {
    console.error('Error saving to cache:', e);
  }
};

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
 * Check if the backend API is running with robust error handling and retry logic
 * specifically designed to handle proxy startup race conditions
 */
export const checkApiHealth = async (maxRetries = 5, initialDelayMs = 500) => {
  // If offline mode is explicitly enabled, return success to prevent repeated checks
  if (isOfflineMode()) {
    return {
      success: true,
      message: 'Operating in offline mode',
      offline: true
    };
  }
  // Create a custom timeout promise
  const timeout = (ms) => {
    return new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error(`Request timed out after ${ms}ms`));
      }, ms);
    });
  };

  // Function to attempt a single health check
  const attemptHealthCheck = async (timeoutMs = 5000, attemptNum = 0) => { // Increased timeout and added attempt parameter
    try {
      // Race between the actual request and a timeout
      const response = await Promise.race([
        apiClient.get('/health'),
        timeout(timeoutMs)
      ]);
      
      // If we get a successful response, cache the fact that the backend is running
      setOfflineMode(false);
      
      return {
        success: true,
        message: response.data?.message || 'API is running',
        status: response.data?.status
      };
    } catch (error) {
      // Only log first attempt failure to avoid console spam
      if (attemptNum === 0) {
        console.warn('Health check attempt failed:', error.message);
      }
      throw error;
    }
  };

  // Try multiple times with increasing backoff
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await attemptHealthCheck(5000 + attempt * 1000, attempt); // Pass attempt number to function
    } catch (error) {
      // If this was the last attempt, enable offline mode and return the error
      if (attempt === maxRetries - 1) {
        // Only log the final failure
        console.info(`All ${maxRetries} health check attempts failed, switching to offline mode`);
        
        // Enable offline mode automatically
        setOfflineMode(true);
        
        return {
          success: false,
          error: 'Backend server is not running. Switched to offline mode.',
          serverDown: true,
          offlineEnabled: true
        };
      }
      
      // Only log every other attempt to reduce console spam
      if (attempt % 2 === 0) {
        console.info(`Health check attempt ${attempt + 1}/${maxRetries} failed, retrying...`);
      }
      
      // Wait before retrying (exponential backoff with jitter)
      const jitter = Math.random() * 300; // Add randomness to prevent synchronized retries
      const delay = Math.pow(2, attempt) * initialDelayMs + jitter; // 500ms, 1000ms, 2000ms, 4000ms, 8000ms + jitter
      
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  // This should never be reached due to the return in the loop, but added for safety
  return {
    success: false,
    error: 'Unexpected error in health check retry logic',
    serverDown: true
  };
};

// Helper function to get data with offline fallback
const getWithOfflineFallback = async (apiCall, cacheKey, offlineData = []) => {
  // If we're in offline mode, try to return cached data first
  if (isOfflineMode()) {
    const cachedData = getCachedData(cacheKey);
    if (cachedData) {
      return {
        success: true,
        ...cachedData.data,
        offline: true,
        timestamp: cachedData.timestamp
      };
    }
    
    // If no cached data available, return empty offline data
    return {
      success: true,
      [cacheKey]: offlineData,
      offline: true,
      message: "Using offline data (no cached data available)"
    };
  }
  
  // If not in offline mode, try the actual API call
  try {
    const result = await apiCall();
    
    // If the call succeeds, cache the result for offline use
    if (result.success) {
      setCachedData(cacheKey, result);
    }
    
    return result;
  } catch (error) {
    // If API call fails, check cache for fallback
    const cachedData = getCachedData(cacheKey);
    if (cachedData) {
      // Temporarily enable offline mode for this session
      setOfflineMode(true);
      
      return {
        success: true,
        ...cachedData.data,
        offline: true,
        timestamp: cachedData.timestamp,
        message: "Using cached data - server is unreachable"
      };
    }
    
    // No cached data available, return error
    return handleApiError(error);
  }
};

// Products API

/**
 * Helper function to make API calls with automatic retries
 * This helps handle temporary network issues or backend startup delays
 */
const callWithRetry = async (apiCall, options = {}) => {
  const { 
    retries = 3, 
    baseDelay = 300, 
    maxDelay = 3000,
    retryIf = (error) => !error.response || error.response.status >= 500 
  } = options;
  
  let lastError;
  
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await apiCall();
    } catch (error) {
      lastError = error;
      
      // Only retry if condition is met (network errors or server errors)
      if (!retryIf(error) || attempt === retries) {
        return handleApiError(error);
      }
      
      // Calculate backoff with jitter
      const jitter = Math.random() * 0.3 + 0.85; // Random value between 0.85 and 1.15
      const delay = Math.min(Math.pow(2, attempt) * baseDelay * jitter, maxDelay);
      
      // Log retry information
      console.info(`API call failed. Retrying in ${Math.round(delay)}ms... (${attempt + 1}/${retries})`);
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  // We should never reach here, but just in case
  return handleApiError(lastError);
};

/**
 * Fetch all tracked products with retry logic and offline fallback
 */
export const getAllProducts = async () => {
  return getWithOfflineFallback(
    async () => {
      const response = await callWithRetry(() => apiClient.get('/products'));
      return response.data || response;
    },
    'products',
    [] // Empty array as fallback for offline mode with no cache
  );
};

/**
 * Fetch a specific product by ID with retry logic and offline fallback
 */
export const getProduct = async (productId) => {
  return getWithOfflineFallback(
    async () => {
      const response = await callWithRetry(() => apiClient.get(`/products/${productId}`));
      return response.data || response;
    },
    `product_${productId}`,
    null // Null as fallback for offline mode with no cache
  );
};

/**
 * Add a new product to track with retry logic
 */
export const addProduct = async (productUrl) => {
  try {
    const response = await callWithRetry(() => apiClient.post('/products', { url: productUrl }));
    return response.data || response;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Delete a product from tracking with retry logic
 */
export const deleteProduct = async (productId) => {
  try {
    const response = await callWithRetry(() => apiClient.delete(`/products/${productId}`));
    return response.data || response;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Get price history for a product with retry logic and offline fallback
 */
export const getPriceHistory = async (productId) => {
  return getWithOfflineFallback(
    async () => {
      const response = await callWithRetry(() => apiClient.get(`/products/${productId}/prices`));
      return response.data || response;
    },
    `price_history_${productId}`,
    [] // Empty array as fallback for offline mode with no cache
  );
};

// Price alerts API

/**
 * Create a price alert for a product with retry logic
 */
export const createPriceAlert = async (productId, email, targetPrice) => {
  try {
    const response = await callWithRetry(() => 
      apiClient.post('/alerts', {
        product_id: productId,
        email,
        target_price: targetPrice
      })
    );
    return response.data || response;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Test a product URL without adding it to the database, with retry logic
 */
export const testProductUrl = async (url) => {
  try {
    const response = await callWithRetry(() => apiClient.post('/test-scraper', { url }));
    return response.data || response;
  } catch (error) {
    return handleApiError(error);
  }
};


// Create a named API service object with all methods
const apiService = {
  getAllProducts,
  getProduct,
  addProduct,
  deleteProduct,
  getPriceHistory,
  createPriceAlert,
  testProductUrl,
  checkApiHealth,
  callWithRetry // Export the retry helper for use in other modules if needed
};

// Export the named object instead of an anonymous object
export default apiService;