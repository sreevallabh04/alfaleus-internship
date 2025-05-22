# PricePulse: Architecture & Flow Diagram

## System Architecture

PricePulse is a full-stack web application with the following main components:

```
                                   ┌───────────────────┐
                                   │    Web Browser    │
                                   └─────────┬─────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             Frontend (React)                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   ┌───────────────────┐ │
│  │  Homepage  │  │   Product   │  │   Price    │   │     Price Drop    │ │
│  │ (Product   │  │   Details   │  │   History  │   │    Alert Form     │ │
│  │  Listing)  │  │    Page     │  │    Chart   │   │                   │ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘   └──────────┬────────┘ │
│        │               │               │                     │          │
│        └───────────────┴───────────────┴─────────────────────┘          │
│                                    │                                     │
└────────────────────────────────────┼─────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             Backend (Flask)                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   ┌───────────────────┐ │
│  │  Product   │  │   Price    │  │ Scheduling │   │    Email Alert    │ │
│  │    API     │  │ History API│  │  Service   │   │      Service      │ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘   └──────────┬────────┘ │
│        │               │               │                     │          │
│        └───────────────┴───────────────┴─────────────────────┘          │
│                                    │                                     │
└────────────────────────────────────┼─────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                             Data Layer                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                         │
│  │  Products  │  │    Price   │  │   Price    │                         │
│  │   Table    │  │  Records   │  │   Alerts   │                         │
│  └────────────┘  └────────────┘  └────────────┘                         │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            External Services                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                         │
│  │   Amazon   │  │  Flipkart  │  │    Email   │                         │
│  │  Website   │  │  Website   │  │   Service  │                         │
│  └────────────┘  └────────────┘  └────────────┘                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Adding a New Product

```
┌──────────┐      ┌───────────┐      ┌───────────┐      ┌───────────┐
│  User    │      │  Frontend │      │  Backend  │      │  Amazon   │
│          │─────▶│           │─────▶│           │─────▶│  Website  │
└──────────┘      └───────────┘      └───────────┘      └───────────┘
                                           │                   │
                                           ▼                   │
                                    ┌───────────┐              │
                                    │ Database  │◀─────────────┘
                                    │           │
                                    └───────────┘
```

1. User enters an Amazon product URL in the form on the homepage
2. Frontend sends the URL to the backend API
3. Backend uses BeautifulSoup/Selenium to scrape product details from Amazon
4. Product information is stored in the database
5. The product is added to the scheduler for regular price tracking

### 2. Automated Price Tracking

```
┌───────────┐      ┌───────────┐      ┌───────────┐
│ Scheduler │      │  Backend  │      │  Amazon   │
│           │─────▶│           │─────▶│  Website  │
└───────────┘      └───────────┘      └───────────┘
                         │                  │
                         ▼                  │
                  ┌───────────┐             │
                  │ Database  │◀────────────┘
                  │           │
                  └───────────┘
```

1. The scheduler runs at regular intervals (every 30-60 minutes)
2. For each tracked product, the scraper fetches the current price
3. The price is recorded in the database with a timestamp
4. Price alerts are checked to see if any thresholds have been met

### 3. Viewing Price History

```
┌──────────┐      ┌───────────┐      ┌───────────┐      ┌───────────┐
│  User    │      │  Frontend │      │  Backend  │      │ Database  │
│          │─────▶│           │─────▶│           │─────▶│           │
└──────────┘      └───────────┘      └───────────┘      └───────────┘
                        ▲                                      │
                        │                                      │
                        └──────────────────────────────────────┘
```

1. User navigates to a product detail page
2. Frontend requests price history from the backend
3. Backend queries the database for all price records for that product
4. Data is returned to the frontend and displayed in a chart

### 4. Creating a Price Alert

```
┌──────────┐      ┌───────────┐      ┌───────────┐      ┌───────────┐
│  User    │      │  Frontend │      │  Backend  │      │ Database  │
│          │─────▶│           │─────▶│           │─────▶│           │
└──────────┘      └───────────┘      └───────────┘      └───────────┘
```

1. User enters email and target price on the product detail page
2. Frontend sends this information to the backend
3. Backend creates a new price alert record in the database

### 5. Sending Price Alert Emails

```
┌───────────┐      ┌───────────┐      ┌───────────┐      ┌───────────┐
│ Scheduler │      │  Backend  │      │ Database  │      │   Email   │
│           │─────▶│           │─────▶│           │      │  Service  │
└───────────┘      └───────────┘      └───────────┘      └───────────┘
                         │                  │                   ▲
                         └──────────────────┘                   │
                                   │                            │
                                   └───────────────────────────▶│
```

1. When checking prices, the backend compares current prices to alert thresholds
2. If a price drops below the target, the alert is triggered
3. The email service sends a notification to the user
4. The alert is marked as sent in the database

## Component Details

### Frontend Components

- **Navbar**: Application header with navigation links
- **HomePage**: Main landing page with product form and list of tracked products
- **ProductForm**: Form for adding new Amazon products
- **ProductCard**: Card display for each tracked product
- **ProductDetailPage**: Detailed view of a single product with price history
- **PriceChart**: Chart visualization of price history using Chart.js
- **PriceAlertForm**: Form for setting up price drop alerts
- **NotFoundPage**: 404 error page for invalid routes

### Backend Components

- **app.py**: Main Flask application with API routes
- **models.py**: Database models for products, price records, and alerts
- **scraper.py**: Web scraping functionality for Amazon products
- **scheduler.py**: Automated job scheduling for price tracking
- **email_service.py**: Email notification functionality for price alerts

### Database Schema

- **Product**: Stores product information (name, URL, image)
- **PriceRecord**: Stores price history with timestamps
- **PriceAlert**: Stores user email and target price thresholds

## Technology Stack

- **Frontend**: React, Chart.js, Bootstrap, Axios
- **Backend**: Flask, SQLAlchemy, APScheduler
- **Database**: SQLite (development) / PostgreSQL (production)
- **Web Scraping**: BeautifulSoup, Selenium
- **Email**: SMTP / SendGrid

## Deployment Diagram

```
┌─────────────────────────────────────┐     ┌─────────────────────────────┐
│           Web Application           │     │        Database Server       │
│ ┌─────────────┐   ┌───────────────┐ │     │                             │
│ │   Frontend  │   │    Backend    │ │     │    ┌─────────────────┐      │
│ │   (React)   │◀──▶│    (Flask)    │◀┼─────┼───▶│     Database     │      │
│ └─────────────┘   └───────────────┘ │     │    └─────────────────┘      │
└─────────────────────────────────────┘     └─────────────────────────────┘
          ▲                   ▲                             
          │                   │                             
          ▼                   ▼                             
┌─────────────────┐     ┌────────────────┐                 
│    Browser      │     │  Email Service │                 
└─────────────────┘     └────────────────┘                 
```

## Bonus Feature: Multi-Platform Comparison (Future Enhancement)

For the bonus multi-platform comparison feature, the architecture would be extended with:

1. A generative AI component to extract product metadata
2. Additional scrapers for other e-commerce platforms
3. A comparison table in the UI

```
┌───────────┐      ┌───────────┐      ┌───────────┐      ┌───────────┐
│ Product   │      │    AI     │      │  Search   │      │  Other    │
│ Metadata  │─────▶│  Service  │─────▶│   Query   │─────▶│ Platforms │
└───────────┘      └───────────┘      └───────────┘      └───────────┘
                                                                │
┌───────────┐                          ┌───────────┐           │
│ Frontend  │◀─────────────────────────│  Backend  │◀──────────┘
└───────────┘                          └───────────┘