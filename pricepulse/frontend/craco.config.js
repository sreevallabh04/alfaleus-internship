/**
 * CRACO (Create React App Configuration Override) configuration
 * This file overrides the default webpack configuration without ejecting
 */
module.exports = {
  webpack: {
    // Add webpack configuration overrides here if needed
  },
  devServer: {
    // Modern setupMiddlewares configuration to replace deprecated options
    setupMiddlewares: (middlewares, devServer) => {
      if (!devServer) {
        throw new Error('webpack-dev-server is not defined');
      }

      // Replace deprecated onBeforeSetupMiddleware
      // Add middleware at the beginning of the middleware stack
      // For example, you can add custom middleware here:
      /*
      middlewares.unshift({
        name: 'custom-middleware',
        middleware: (req, res, next) => {
          // Custom middleware logic
          next();
        },
      });
      */

      // Replace deprecated onAfterSetupMiddleware
      // Add middleware after the app middleware
      middlewares.push({
        name: 'check-backend-middleware',
        middleware: (req, res, next) => {
          // If this is a direct request to check backend health
          if (req.url === '/__backend_health') {
            const http = require('http');
            
            // Simple HTTP request to check if backend is running
            const checkRequest = http.request({
              host: 'localhost',
              port: 5000,
              path: '/api/health',
              method: 'GET',
              timeout: 3000,
            }, (response) => {
              res.writeHead(200, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ 
                backendRunning: true,
                status: response.statusCode
              }));
            });
            
            checkRequest.on('error', (error) => {
              res.writeHead(200, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ 
                backendRunning: false,
                error: error.message
              }));
            });
            
            checkRequest.end();
            return;
          }
          
          next();
        },
      });

      return middlewares;
    },
  },
};