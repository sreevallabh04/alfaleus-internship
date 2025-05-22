# PricePulse - E-Commerce Price Tracker & Smart Comparator

PricePulse is a full-stack web application that allows users to track Amazon product prices, view price history, and receive alerts when prices drop below a specified threshold.

![PricePulse Screenshot](https://via.placeholder.com/800x450?text=PricePulse+Screenshot)

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

## Setup Instructions

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
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables by creating a `.env` file in the backend directory with the following contents:
   ```
   DATABASE_URI=sqlite:///pricepulse.db
   SCHEDULER_INTERVAL_MINUTES=60
   EMAIL_HOST=smtp.example.com
   EMAIL_PORT=587
   EMAIL_USERNAME=your_email@example.com
   EMAIL_PASSWORD=your_app_password
   EMAIL_FROM=your_email@example.com
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

## Important Notes

1. **Both Services Must Be Running**: Both the backend and frontend servers need to be running for the application to work properly.

2. **First Run Database**: The first time you run the application, the database will be automatically created with the necessary tables.

3. **Email Configuration**: To enable price drop alerts, ensure you've set up proper SMTP settings in the `.env` file.

4. **Web Scraping Limitations**: Amazon may block excessive scraping attempts. The application implements best practices to avoid being blocked, but be mindful of adding too many products.

## Troubleshooting

### "Server Error" When Loading Products

If you see a "Server Error" when trying to load products, ensure:

1. The backend Flask server is running at http://localhost:5000
2. Your internet connection is active
3. The database has been properly initialized
4. No firewall is blocking connections between frontend and backend

You can verify the backend is running by accessing http://localhost:5000/api/health in your browser, which should return a JSON response indicating the API is running.

### Scraping Issues

If product details aren't being fetched correctly:

1. Check that the Amazon URL is valid
2. Ensure you're not being rate-limited by Amazon
3. Try adding a user-agent in the scraper.py file if needed

## Architecture

For a detailed overview of the system architecture, check the [architecture.md](./architecture.md) file.

## Development

The architecture follows clean separation of concerns:
- Backend API handles data persistence, scheduled jobs, and web scraping
- Frontend provides an intuitive user interface and data visualization
- Communication happens via RESTful API endpoints

## License

[MIT License](LICENSE)