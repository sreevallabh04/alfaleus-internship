import { useState, useCallback } from 'react';
import { ProductData, ProductDetails } from '../types';
import { getProducts, addProduct, deleteProduct, getPriceHistory } from '../services/api';

export const useProducts = () => {
  const [products, setProducts] = useState<ProductData[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<ProductDetails | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchProducts = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await getProducts();
      setProducts(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch products. Please try again later.');
      console.error('Error fetching products:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleAddProduct = useCallback(async (amazonUrl: string, targetPrice: number, email: string) => {
    try {
      setIsLoading(true);
      const newProduct = await addProduct(amazonUrl, targetPrice, email);
      setProducts(prevProducts => [...prevProducts, newProduct]);
      setError(null);
    } catch (err) {
      setError('Failed to add product. Please try again.');
      console.error('Error adding product:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleDeleteProduct = useCallback(async (productId: number) => {
    try {
      await deleteProduct(productId);
      setProducts(prevProducts => prevProducts.filter(p => p.id !== productId));
      if (selectedProduct?.id === productId) {
        setSelectedProduct(null);
      }
      setError(null);
    } catch (err) {
      setError('Failed to delete product. Please try again.');
      console.error('Error deleting product:', err);
    }
  }, [selectedProduct]);

  const handleSelectProduct = useCallback(async (productId: number) => {
    try {
      setIsLoading(true);
      const [product, priceHistory] = await Promise.all([
        getProducts().then(products => products.find(p => p.id === productId)),
        getPriceHistory(productId)
      ]);

      if (product) {
        setSelectedProduct({
          ...product,
          priceHistory
        });
      }
      setError(null);
    } catch (err) {
      setError('Failed to fetch product details. Please try again.');
      console.error('Error fetching product details:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleRefreshData = useCallback(async () => {
    if (selectedProduct) {
      try {
        setIsRefreshing(true);
        const [product, priceHistory] = await Promise.all([
          getProducts().then(products => products.find(p => p.id === selectedProduct.id)),
          getPriceHistory(selectedProduct.id)
        ]);

        if (product) {
          setSelectedProduct({
            ...product,
            priceHistory
          });
        }
        setError(null);
      } catch (err) {
        setError('Failed to refresh data. Please try again.');
        console.error('Error refreshing data:', err);
      } finally {
        setIsRefreshing(false);
      }
    }
  }, [selectedProduct]);

  return {
    products,
    selectedProduct,
    isLoading,
    error,
    isRefreshing,
    fetchProducts,
    handleAddProduct,
    handleDeleteProduct,
    handleSelectProduct,
    handleRefreshData
  };
}; 