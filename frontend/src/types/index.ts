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

export interface ApiResponse {
  success: boolean
  message?: string
}
