# Fix for Webpack Dev Server Deprecation Warnings

## Issue

Create React App (CRA) v5.0.1 uses webpack-dev-server v4.x.x, which shows deprecation warnings for:
- `onBeforeSetupMiddleware` 
- `onAfterSetupMiddleware`

These options are deprecated in favor of the new `setupMiddlewares` API.

## Solution Options

Since CRA manages webpack configuration internally, you have three options:

### Option 1: Use CRACO (Create React App Configuration Override)

This allows you to customize webpack config without ejecting:

1. Install CRACO:
```bash
npm install @craco/craco --save-dev
```

2. Create a `craco.config.js` file in the frontend root directory:
```javascript
module.exports = {
  devServer: {
    // Configure dev server options
    setupMiddlewares: (middlewares, devServer) => {
      // Add custom middleware or modify existing ones
      if (!devServer) {
        throw new Error('webpack-dev-server is not defined');
      }
      
      // Your middleware setup here
      
      return middlewares;
    },
  },
};
```

3. Update package.json scripts to use CRACO:
```json
"scripts": {
  "start": "craco start",
  "build": "craco build",
  "test": "craco test"
}
```

### Option 2: Upgrade to React Scripts v5.0.2+ 

If available, upgrading to a newer version of react-scripts may include fixes for these deprecation warnings.

```bash
npm install react-scripts@latest --save
```

### Option 3: Customize setupProxy.js

While not removing the deprecation warnings completely, you can ensure your proxy setup uses the current API pattern:

```javascript
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Your existing proxy setup
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
    })
  );
  
  // Add any additional middleware here
};
```

## Recommendation

Start with Option 1 (CRACO) as it's the least invasive approach that still allows you to customize the webpack configuration without ejecting from CRA.

If you encounter issues with CRACO, consider Option 2 (upgrading react-scripts) if a newer version is available.

Option 3 is the most limited but also the simplest if you just want to ensure your proxy configuration works properly.