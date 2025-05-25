export interface Product {
  id: number
  name: string
  url: string
  image_url: string
  description: string
  current_price: number
  currency: string
  created_at: string
  updated_at: string
}

export interface PriceRecord {
  id: number
  product_id: number
  price: number
  timestamp: string
}

export interface PriceAlert {
  id: number
  product_id: number
  email: string
  target_price: number
  triggered: boolean
  created_at: string
}

export interface GroupedPriceHistory {
  [platform: string]: PriceRecord[];
}

export interface ApiResponse {
  success: boolean;
  message?: string;
  // Add specific types for different API responses if needed,
  // or make this more generic. For now, adding price_history for product detail.
  product?: Product; // For getProduct response
  price_history?: GroupedPriceHistory; // For getProduct response
  products?: Product[]; // For getAllProducts response
  alert?: PriceAlert; // For createAlert response
  comparisons?: any[]; // Add type for comparison results if needed
  metadata?: any; // Add type for comparison metadata if needed
  is_mock_data?: boolean; // For comparison response
}
