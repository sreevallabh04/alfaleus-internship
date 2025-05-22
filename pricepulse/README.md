# PricePulse - E-Commerce Price Tracker & Smart Comparator

PricePulse is a full-stack web application that allows users to track Amazon product prices, view price history, and receive alerts when prices drop below a specified threshold.

## Features

- **Amazon Product Tracking**: Add any Amazon product URL to track its price
- **Price History Visualization**: View price trends with interactive charts
- **Price Drop Alerts**: Get email notifications when prices drop below your target
- **Automatic Price Updates**: System automatically checks prices at regular intervals

## Tech Stack

### Frontend
- React.js with hooks for UI components
- Bootstrap for responsive design
- Chart.js for price history visualization
- Axios for API communication

### Backend
- Flask (Python) RESTful API
- SQLAlchemy for database ORM
- BeautifulSoup/Selenium for web scraping
- APScheduler for automated price checking

## Quick Start Guide

### Option 1: Unified Startup Script (Recommended)

The easiest way to run the application is using our unified Python startup script:

```bash
python start_app.py
```

This script will:
- Check all prerequisites
- Start the backend server
- Start the frontend server
- Open the application in your browser
- Provide an easy way to stop both servers (Ctrl+C)

### Option 2: Separate Startup Scripts

We've also provided separate scripts for both Windows and Linux/Mac users:

#### Windows Users

1. Start the backend server first:
   - Double-click `start_backend.bat` or run it from command prompt
   - Wait until you see "Running on http://0.0.0.0:5000"

2. Start the frontend server:
   - Double-click `start_frontend.bat` or run it from command prompt
   - A browser window should automatically open at http://localhost:3000

#### Linux/Mac Users

1. Make the scripts executable:
   ```bash
   chmod +x start_backend.sh start_frontend.sh
   ```

2. Start the backend server first:
   ```bash
   ./start_backend.sh
   ```

3. In a new terminal window, start the frontend server:
   ```bash
   ./start_frontend.sh
   ```

## Detailed Setup Instructions

If you prefer to set up manually or encounter issues with the scripts, follow these detailed instructions:

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd pricepulse/backend
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables by editing the `.env` file in the backend directory:
   ```
   DATABASE_URI=sqlite:///pricepulse.db
   SCHEDULER_INTERVAL_MINUTES=60
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   EMAIL_FROM=your_email@gmail.com
   ```

5. Run the Flask backend server:
   ```bash
   python app.py
   ```

   The backend should now be running at http://localhost:5000

### Frontend Setup

1. Open a new terminal window and navigate to the frontend directory:
   ```bash
   cd pricepulse/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or if you're using yarn
   yarn install
   ```

3. Start the development server:
   ```bash
   npm start
   # or with yarn
   yarn start
   ```

   The frontend should now be running at http://localhost:3000

## Troubleshooting Common Issues

### "Backend server is not running" Error

If you see this error message in the application:

1. Verify the backend is running:
   - Check if the Flask server is running in a terminal
   - Verify it's accessible at http://localhost:5000/api/health
   - If not running, start it using the instructions above

2. Check for Python environment issues:
   - Ensure all requirements are installed (`pip install -r requirements.txt`)
   - Try creating a fresh virtual environment if you encounter import errors

3. Check for port conflicts:
   - If port 5000 is already in use, edit the `app.py` file to use a different port
   - Update the frontend proxy configuration accordingly

### Chrome/Selenium Issues

The web scraper uses Selenium with Chrome as a fallback method. If you encounter issues:

1. Install Chrome browser if not already installed
2. The app includes fallback mechanisms, but if scraping fails entirely:
   - Check your internet connection
   - Verify Amazon is accessible from your location
   - Try using a different URL format (product URLs can vary by region)

### Email Alerts Not Working

1. Verify your email configuration in the `.env` file
2. For Gmail, you need to:
   - Enable "Less secure app access" or
   - Use an App Password if you have 2-factor authentication enabled
3. Test your email configuration by setting a price alert

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in the backend `.env` file
2. Configure a production database (PostgreSQL recommended)
3. Set up a proper WSGI server (e.g., Gunicorn) for the Flask backend
4. Build the React frontend: `npm run build`
5. Serve the frontend build using Nginx or another web server
6. Configure proper CORS settings between your frontend and backend servers

## Architecture

For a detailed overview of the system architecture, check the [architecture.md](./architecture.md) file.

## License

This project is licensed under the MIT License.