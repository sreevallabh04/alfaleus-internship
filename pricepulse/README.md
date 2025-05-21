# PricePulse - E-Commerce Price Tracker & Smart Comparator

PricePulse is a full-stack web application that allows users to track Amazon product prices over time and visualize price trends. Users can enter an Amazon product URL and the application will automatically track and record the product's price at regular intervals, displaying the price history in a graph.

## Features

### Core Features
- Enter Amazon product URL for tracking
- Automatic price tracking every hour
- Price history visualization with interactive graphs
- Current price display with product details (name and image)

### Bonus Features
- Multi-platform price comparison using AI (Flipkart, Meesho, etc.)
- Price drop email alerts when prices fall below a target

## Tech Stack

### Backend
- Flask (Python)
- SQLite Database
- APScheduler for scheduled scraping
- BeautifulSoup for web scraping

### Frontend
- React
- Chart.js for data visualization
- Axios for API requests

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 14+
- pip
- npm

### Backend Setup
1. Navigate to the backend directory:
```
cd pricepulse/backend
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run the Flask server:
```
python app.py
```

### Frontend Setup
1. Navigate to the frontend directory:
```
cd pricepulse/frontend
```

2. Install dependencies:
```
npm install
```

3. Start the development server:
```
npm start
```

## Usage
1. Open the application in your browser
2. Enter an Amazon product URL in the input field
3. Click "Start Tracking" to begin monitoring the price
4. View the price history graph and current product details
5. (Optional) Set up price drop alerts by entering your email and target price

## Project Structure
```
pricepulse/
├── backend/
│   ├── app.py                  # Main Flask application
│   ├── scraper.py              # Web scraping functionality
│   ├── scheduler.py            # APScheduler setup
│   ├── models.py               # Database models
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── public/                 # Static assets
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API services
│   │   ├── pages/              # Main pages
│   │   ├── App.js              # Main application component
│   │   └── index.js            # Entry point
│   ├── package.json            # Node.js dependencies
│   └── README.md               # Frontend documentation
└── README.md                   # Project documentation
```

## License
This project is licensed under the MIT License