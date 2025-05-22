import { render, screen } from '@testing-library/react';
import App from './App';

test('renders without crashing', () => {
  render(<App />);
  // Basic test to verify the app loads without crashing
  const linkElement = screen.getByText(/PricePulse/i);
  expect(linkElement).toBeInTheDocument();
});