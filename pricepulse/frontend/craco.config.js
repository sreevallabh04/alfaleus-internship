/**
 * CRACO (Create React App Configuration Override) configuration
 * This file overrides the default webpack configuration without ejecting
 */
const ESLintWebpackPlugin = require('eslint-webpack-plugin');
const path = require('path');

module.exports = {
  webpack: {
    plugins: {
      // Remove any existing ESLint plugins (including deprecated eslint-loader)
      remove: [
        'ESLintWebpackPlugin',
        'eslint-loader'
      ],
      // Add the modern ESLint webpack plugin
      add: [
        new ESLintWebpackPlugin({
          extensions: ['js', 'jsx', 'ts', 'tsx'],
          eslintPath: require.resolve('eslint'),
          context: path.resolve(__dirname, 'src'),
          cache: true,
          cacheLocation: path.resolve(__dirname, 'node_modules/.cache/.eslintcache'),
          emitWarning: true,
          emitError: false,
          failOnError: false,
          failOnWarning: false,
          quiet: false,
          outputReport: false
        })
      ]
    }
  },
  devServer: {
    // Modern setupMiddlewares configuration replacing deprecated options
    setupMiddlewares: (middlewares, devServer) => {
      if (!devServer) {
        throw new Error('webpack-dev-server is not defined');
      }

      // Add custom backend health check middleware
      middlewares.push({
        name: 'backend-health-check',
        path: '/__backend_health',
        middleware: async (req, res, next) => {
          if (req.url !== '/__backend_health') {
            return next();
          }

          // Set CORS headers for frontend requests
          res.setHeader('Access-Control-Allow-Origin', '*');
          res.setHeader('Access-Control-Allow-Methods', 'GET');
          res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
          res.setHeader('Content-Type', 'application/json');

          try {
            // Use fetch API (available in Node.js 18+) or fall back to http module
            let backendResponse;
            
            if (typeof fetch !== 'undefined') {
              // Modern approach using fetch
              const controller = new AbortController();
              const timeoutId = setTimeout(() => controller.abort(), 3000);
              
              try {
                backendResponse = await fetch('http://127.0.0.1:5000/api/health', {
                  method: 'GET',
                  signal: controller.signal,
                  headers: {
                    'Accept': 'application/json'
                  }
                });
                clearTimeout(timeoutId);
                
                const responseData = {
                  backendRunning: true,
                  status: backendResponse.status,
                  statusText: backendResponse.statusText,
                  timestamp: new Date().toISOString()
                };
                
                res.status(200).json(responseData);
              } catch (fetchError) {
                clearTimeout(timeoutId);
                throw fetchError;
              }
            } else {
              // Fallback to http module for older Node.js versions
              const http = require('http');
              
              const healthCheckPromise = new Promise((resolve, reject) => {
                const request = http.request({
                  hostname: '127.0.0.1',
                  port: 5000,
                  path: '/api/health',
                  method: 'GET',
                  timeout: 3000,
                  headers: {
                    'Accept': 'application/json'
                  }
                }, (response) => {
                  resolve({
                    status: response.statusCode,
                    statusText: response.statusMessage
                  });
                });
                
                request.on('error', reject);
                request.on('timeout', () => {
                  request.destroy();
                  reject(new Error('Request timeout'));
                });
                
                request.end();
              });
              
              const result = await healthCheckPromise;
              const responseData = {
                backendRunning: true,
                status: result.status,
                statusText: result.statusText,
                timestamp: new Date().toISOString()
              };
              
              res.status(200).json(responseData);
            }
          } catch (error) {
            // Backend is not reachable or error occurred
            const errorResponse = {
              backendRunning: false,
              error: error.message,
              errorType: error.name || 'UnknownError',
              timestamp: new Date().toISOString()
            };
            
            res.status(200).json(errorResponse);
          }
        }
      });

      return middlewares;
    },
    
    // Additional modern dev server options
    hot: true,
    liveReload: true,
    compress: true,
    historyApiFallback: {
      disableDotRule: true,
    },
    client: {
      overlay: {
        errors: true,
        warnings: false,
      },
      progress: true,
    }
  }
};