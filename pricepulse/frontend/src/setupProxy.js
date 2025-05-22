const { createProxyMiddleware } = require('http-proxy-middleware');

/**
 * Modern setupProxy configuration for webpack-dev-server v4+
 * This replaces the deprecated onBeforeSetupMiddleware and onAfterSetupMiddleware
 */
module.exports = function(app) {
  // Create proxy middleware with enhanced error handling
  const apiProxy = createProxyMiddleware({
    target: 'http://localhost:5000',
    changeOrigin: true,
    // Add proper error handling
    onError: (err, req, res) => {
      console.warn('Proxy error:', err.message);
      
      // Send a more user-friendly error response
      res.writeHead(502, {
        'Content-Type': 'application/json',
      });
      
      res.end(JSON.stringify({
        success: false,
        error: 'Cannot connect to backend server. Please ensure the backend server is running on port 5000.',
        serverDown: true
      }));
    },
    // Add request/response logging for debugging
    onProxyRes: (proxyRes, req, res) => {
      // Log successful requests for debugging
      if (proxyRes.statusCode < 400) {
        console.debug(`Proxy: ${req.method} ${req.path} -> ${proxyRes.statusCode}`);
      } else {
        console.warn(`Proxy error: ${req.method} ${req.path} -> ${proxyRes.statusCode}`);
      }
    },
    // Add larger timeout for long-running requests (like scraping)
    proxyTimeout: 30000,
    // Retry on connection errors
    pathRewrite: {
      '^/api': '/api'  // Identity rewrite (no change)
    }
  });
  
  // Apply the proxy middleware to /api routes
  app.use('/api', apiProxy);
  
  // Add health endpoint to check if backend is running
  app.use('/api/health-check', (req, res, next) => {
    // First try to pass to actual backend
    apiProxy(req, res, (err) => {
      if (err) {
        // If error, respond with backend down status
        res.json({
          success: false,
          message: 'Backend server is not running',
          serverDown: true
        });
      }
    });
  });
};