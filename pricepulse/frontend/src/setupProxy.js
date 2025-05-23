const { createProxyMiddleware } = require('http-proxy-middleware');

/**
 * Modern setupProxy configuration for webpack-dev-server v4+
 * with improved error handling and reconnection logic
 */
module.exports = function(app) {
  // Configuration for the proxy middleware
  const apiProxyConfig = {
    target: 'http://127.0.0.1:5000',
    changeOrigin: true,
    
    // Increase timeouts for long-running requests (like scraping)
    proxyTimeout: 60000,         // 1 minute
    connectTimeout: 10000,       // 10 seconds
    
    // Retry logic
    retry: 3,                    // Try 3 times
    
    // Wait between retries (ms)
    retryDelay: 1000,            
    
    // Don't throw on proxy errors, handle them gracefully
    secure: false,
    xfwd: true,
    
    // Enhanced error handling
    onError: (err, req, res) => {
      console.warn(`Proxy error for ${req.method} ${req.path}:`, err.message);
      
      // Send a user-friendly error response
      res.writeHead(502, {
        'Content-Type': 'application/json',
      });
      
      res.end(JSON.stringify({
        success: false,
        error: 'Cannot connect to backend server. Please ensure the backend server is running on port 5000.',
        serverDown: true,
        errorDetails: err.message
      }));
    },
    
    // Log requests for debugging
    onProxyRes: (proxyRes, req, res) => {
      if (proxyRes.statusCode < 400) {
        console.debug(`Proxy: ${req.method} ${req.path} -> ${proxyRes.statusCode}`);
      } else {
        console.warn(`Proxy response error: ${req.method} ${req.path} -> ${proxyRes.statusCode}`);
      }
    },
    
    // Log proxy requests
    onProxyReq: (proxyReq, req, res) => {
      const requestInfo = {
        method: req.method,
        path: req.path,
        timestamp: new Date().toISOString()
      };
      
      // Debug mode only
      if (process.env.NODE_ENV === 'development') {
        console.debug(`Proxy request: ${JSON.stringify(requestInfo)}`);
      }
    },
    
    // Path rewrite - identity mapping
    pathRewrite: {
      '^/api': '/api'  // No change to path
    }
  };
  
  // Create the proxy middleware
  const apiProxy = createProxyMiddleware(apiProxyConfig);
  
  // Apply the proxy middleware to /api routes
  app.use('/api', apiProxy);
  
  // Enhanced health endpoint to check if backend is running
  app.use('/__backend_health', (req, res) => {
    const http = require('http');
    
    // Make a direct health check request to backend
    const checkRequest = http.request({
      host: '127.0.0.1',
      port: 5000,
      path: '/api/health',
      method: 'GET',
      timeout: 5000, // 5 second timeout
    }, (response) => {
      // Read response data
      let data = '';
      response.on('data', (chunk) => {
        data += chunk;
      });
      
      response.on('end', () => {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          backendRunning: true,
          status: response.statusCode,
          response: data
        }));
      });
    });
    
    // Handle request errors
    checkRequest.on('error', (error) => {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ 
        backendRunning: false,
        error: error.message,
        advice: 'Please ensure the backend server is running on port 5000'
      }));
    });
    
    checkRequest.end();
  });
};