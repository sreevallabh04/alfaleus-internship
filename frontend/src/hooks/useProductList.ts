import { useCallback } from 'react';
import { ProductData } from '../types';
import { formatPrice, calculateSavings, calculateSavingsPercentage } from '../utils/helpers';

interface UseProductListProps {
  products: ProductData[];
  selectedProductId?: number;
  onDeleteProduct: (productId: number) => Promise<void>;
  onSelectProduct: (productId: number) => Promise<void>;
}

export const useProductList = ({
  products,
  selectedProductId,
  onDeleteProduct,
  onSelectProduct
}: UseProductListProps) => {
  const handleDelete = useCallback(async (productId: number) => {
    try {
      await onDeleteProduct(productId);
    } catch (error) {
      // Error handling is done in the parent component
    }
  }, [onDeleteProduct]);

  const handleSelect = useCallback(async (productId: number) => {
    try {
      await onSelectProduct(productId);
    } catch (error) {
      // Error handling is done in the parent component
    }
  }, [onSelectProduct]);

  const getProductStats = useCallback((product: ProductData) => {
    const savings = calculateSavings(product.current_price, product.target_price);
    const savingsPercentage = calculateSavingsPercentage(product.current_price, product.target_price);
    const isPriceBelowTarget = product.current_price <= product.target_price;

    return {
      savings,
      savingsPercentage,
      isPriceBelowTarget,
      formattedCurrentPrice: formatPrice(product.current_price),
      formattedTargetPrice: formatPrice(product.target_price),
      formattedSavings: formatPrice(savings)
    };
  }, []);

  return {
    handleDelete,
    handleSelect,
    getProductStats
  };
}; 