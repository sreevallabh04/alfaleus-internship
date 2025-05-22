# PricePulse Project Report

## Project Overview

PricePulse is a web application designed to track and monitor product prices from e-commerce platforms, primarily Amazon. The application allows users to add products they're interested in, view price history over time, and set price alerts to be notified when prices drop below their desired threshold.

**Completion Status:** 90% Complete

## System Architecture

PricePulse follows a client-server architecture with clear separation of concerns:

### Frontend (React.js)
- Single-page application built with React and Create React App
- State management handled via React hooks
- UI components using React Bootstrap for responsive design
- Charts and animations using Chart.js and Framer Motion
- Offline-capable with localStorage-based caching

### Backend (Python/Flask)
- RESTful API built with Flask
- SQLite database with SQLAlchemy ORM
- Web scraping functionality using BeautifulSoup and Requests
- Scheduled price updates using APScheduler
- Email notifications for price alerts

### Communication
- Frontend communicates with backend via RESTful API calls
- Proxy middleware to handle cross-origin requests in development
- Error handling and automatic retries for API resilience

## Key Features Implemented

### Product Tracking
- ✅ URL input and validation for Amazon product links
- ✅ Product information extraction (name, price, image)
- ✅ Persistent storage of product data
- ✅ Price history tracking and visualization
- ✅ Scheduled background price updates

### User Interface
- ✅ Responsive dashboard with product cards
- ✅ Detailed product view with price history chart
- ✅ Interactive price charts with time filtering
- ✅ Loading states and animations
- ✅ Toast notifications for user feedback
- ✅ Offline mode indicator and functionality

### Price Alerts
- ✅ Email-based price alert system
- ✅ Target price setting for alerts
- ✅ Email delivery when prices drop below target

### Error Handling & Resilience
- ✅ Robust error handling for web scraping
- ✅ API error handling with meaningful messages
- ✅ Offline mode with cached data
- ✅ Connection retry mechanisms
- ✅ Backend health checks

## Technical Implementation Details

### Frontend Implementation

The frontend is built using modern React practices:

#### Component Structure
```
frontend/
├── public/              # Static assets
└── src/
    ├── components/      # Reusable UI components
    │   ├── common/      # Shared components (Loader, EmptyState, etc.)
    │   ├── layout/      # Layout components (Navbar)
    │   └── products/    # Product-specific components
    ├── pages/           # Page components
    ├── services/        # API service layer
    └── App.js           # Main application component
```

#### Key Technologies Used
- **React 18**: For building the user interface
- **React Router 6**: For client-side routing
- **React Bootstrap**: For responsive UI components
- **Chart.js/react-chartjs-2**: For price history visualization
- **Axios**: For API communication
- **React Toastify**: For toast notifications
- **Framer Motion**: For UI animations
- **CRACO**: For webpack configuration overrides

#### State Management
The application uses React's built-in state management capabilities:
- Local component state with `useState` for UI-specific state
- `useEffect` and `useCallback` for side effects and memoization
- Context API could be added for global state if needed

### Backend Implementation

The backend is built with Python/Flask:

#### Code Structure
```
backend/
├── app.py              # Main Flask application
├── models.py           # Database models
├── scraper.py          # Web scraping functionality
├── scheduler.py        # Price update scheduler
├── email_service.py    # Email notification service
└── instance/           # Database files
```

#### Key Technologies Used
- **Flask**: Lightweight web framework
- **SQLAlchemy**: ORM for database operations
- **BeautifulSoup**: For HTML parsing and scraping
- **Requests**: For HTTP requests
- **APScheduler**: For scheduled price updates
- **SMTP/Email**: For sending price alert notifications

#### Database Schema
Three main models:
1. **Product**: Stores product information (name, URL, image)
2. **PriceRecord**: Stores price history for products
3. **PriceAlert**: Stores user email and target price for alerts

## Issues Addressed & Solutions

### 1. React ESLint Warning (react-hooks/exhaustive-deps)
**Issue**: The `useEffect` hook in ProductDetailPage.js was missing a dependency.

**Solution**: 
- Implemented `useCallback` for the `fetchProductData` function
- Added it to the `useEffect` dependency array
- Ensured correct dependencies to prevent unnecessary re-fetching

### 2. Proxy Errors (ECONNREFUSED)
**Issue**: The React dev server would fail with proxy errors when the backend wasn't running.

**Solution**:
- Enhanced proxy configuration with proper error handling
- Implemented offline mode with localStorage caching
- Added UI indicators for backend connection status
- Created automatic retry mechanisms
- Added comprehensive backend health checking

### 3. Webpack Dev Server Deprecation Warnings
**Issue**: CRA was using deprecated Webpack Dev Server options.

**Solution**:
- Implemented CRACO configuration to override webpack settings
- Used modern `setupMiddlewares` API instead of deprecated options
- Updated package.json scripts to use CRACO
- Modified start scripts to ensure CRACO installation

### 4. Product Scraping Issues
**Issue**: Selenium-based scraping was causing server errors.

**Solution**:
- Removed Selenium dependency
- Enhanced requests-based scraping with multiple retry strategies
- Implemented multiple parsing approaches (JSON-LD, HTML selectors, regex)
- Added URL normalization for different Amazon URL formats
- Improved error handling and validation

## Technical Debt and Improvements

### Current Technical Debt
- Limited test coverage
- No authentication system
- Single e-commerce platform support (Amazon only)
- Basic error logging without centralized monitoring
- No CI/CD pipeline configuration

### Recommended Future Enhancements
1. **Expanded Platform Support**
   - Add support for other e-commerce platforms (Flipkart, Meesho, etc.)
   - Implement platform-specific scrapers

2. **User Authentication**
   - Add user accounts with registration/login
   - Personalized dashboards and saved products

3. **Enhanced Notifications**
   - Push notifications for price drops
   - Browser notifications
   - Customizable notification settings

4. **Advanced Analytics**
   - Price trend analysis
   - Price prediction using historical data
   - Best time to buy recommendations

5. **Performance Optimization**
   - Implement server-side rendering for initial load
   - Add PWA capabilities for offline use
   - Optimize image loading and caching

6. **Testing & Quality**
   - Add comprehensive unit and integration tests
   - Implement end-to-end testing
   - Set up CI/CD pipeline

## Setup and Running Instructions

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- npm or yarn

### Running the Backend
```bash
# Windows
start_backend.bat

# Unix/Linux
./start_backend.sh
```

### Running the Frontend
```bash
# Windows
start_frontend.bat

# Unix/Linux
./start_frontend.sh
```

## Conclusion

PricePulse is a robust web application that successfully implements product price tracking, visualization, and alerting functionality. The application is built using modern web technologies and follows best practices for web development. The system architecture is designed for maintainability and scalability, with clear separation of concerns.

The application provides a good user experience with responsive design, interactive charts, and helpful feedback. The implementation includes error handling, offline capabilities, and connection resilience to ensure the application works well even in non-ideal conditions.

While there are some areas for improvement and potential future enhancements, the current implementation provides a solid foundation for a production-ready price tracking application.