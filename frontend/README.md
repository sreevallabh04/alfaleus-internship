# PricePulse Frontend

This is the frontend application for PricePulse, a price tracking application for Amazon products.

## Features

- Track Amazon product prices
- Set target prices and receive email notifications
- View price history with interactive charts
- Dark mode support
- Responsive design

## Tech Stack

- React 18
- TypeScript
- Tailwind CSS
- Chart.js
- Axios

## Prerequisites

- Node.js 16.x or later
- npm 7.x or later

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env` file in the root directory with the following variables:
   ```
   REACT_APP_API_URL=http://localhost:5000
   REACT_APP_GITHUB_URL=https://github.com/yourusername/pricepulse
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The application will be available at http://localhost:3000.

## Building for Production

To create a production build:

```bash
npm run build
```

The build artifacts will be stored in the `build/` directory.

## Project Structure

```
src/
  ├── components/     # React components
  ├── types/         # TypeScript type definitions
  ├── services/      # API services
  ├── utils/         # Utility functions
  ├── App.tsx        # Main application component
  └── index.tsx      # Application entry point
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 