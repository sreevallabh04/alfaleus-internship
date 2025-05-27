# PricePulse

PricePulse is a web application that helps users track Amazon product prices and get notified when prices drop below their target price.

## Features

- Track Amazon product prices
- Set target prices for products
- Receive email notifications when prices drop
- View price history and trends
- Compare prices across different platforms
- Responsive and modern UI

## Tech Stack

### Backend
- Flask (Python web framework)
- SQLAlchemy (ORM)
- APScheduler (Task scheduling)
- BeautifulSoup4 (Web scraping)
- Flask-CORS (Cross-origin resource sharing)

### Frontend
- React (UI library)
- TypeScript
- Chart.js (Data visualization)
- Tailwind CSS (Styling)
- Axios (HTTP client)

## Setup

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the backend directory with the following variables:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
```

4. Run the backend server:
```bash
python app.py
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

## API Endpoints

### Products
- `POST /api/products` - Add a new product to track
- `GET /api/products` - Get all tracked products
- `GET /api/products/<id>` - Get details of a specific product
- `GET /api/products/<id>/history` - Get price history for a product
- `DELETE /api/products/<id>` - Delete a tracked product

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 