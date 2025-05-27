import React from 'react';
import { ProductData } from '../types';
import { useProductList } from '../hooks/useProductList';

interface ProductListProps {
  products: ProductData[];
  onDeleteProduct: (productId: number) => Promise<void>;
  onSelectProduct: (productId: number) => Promise<void>;
  selectedProductId?: number;
}

const ProductList: React.FC<ProductListProps> = ({
  products,
  onDeleteProduct,
  onSelectProduct,
  selectedProductId
}) => {
  const { handleDelete, handleSelect, getProductStats } = useProductList({
    products,
    selectedProductId,
    onDeleteProduct,
    onSelectProduct
  });

  if (products.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center">
        <p className="text-gray-600 dark:text-gray-400">
          No products being tracked. Add a product to get started!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {products.map((product) => {
        const {
          savings,
          savingsPercentage,
          isPriceBelowTarget,
          formattedCurrentPrice,
          formattedTargetPrice,
          formattedSavings
        } = getProductStats(product);

        return (
          <div
            key={product.id}
            className={`bg-white dark:bg-gray-800 rounded-lg shadow p-4 transition-colors cursor-pointer ${
              selectedProductId === product.id
                ? 'ring-2 ring-blue-500'
                : 'hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
            onClick={() => handleSelect(product.id)}
          >
            <div className="flex items-start space-x-4">
              <img
                src={product.image_url}
                alt={product.title}
                className="w-20 h-20 object-contain rounded"
              />
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {product.title}
                </h3>
                <div className="mt-1 flex items-center space-x-2">
                  <span className="text-lg font-semibold text-gray-900 dark:text-white">
                    {formattedCurrentPrice}
                  </span>
                  {isPriceBelowTarget && (
                    <span className="text-sm text-green-600 dark:text-green-400">
                      Save {formattedSavings} ({savingsPercentage}%)
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Target: {formattedTargetPrice}
                </p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(product.id);
                }}
                className="p-2 text-gray-400 hover:text-red-500 focus:outline-none"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default ProductList; 