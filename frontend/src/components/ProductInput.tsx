import React from 'react';
import { useProductInput } from '../hooks/useProductInput';

interface ProductInputProps {
  onAddProduct: (amazonUrl: string, targetPrice: number, email: string) => Promise<void>;
}

const ProductInput: React.FC<ProductInputProps> = ({ onAddProduct }) => {
  const { state, handleChange, handleSubmit } = useProductInput(onAddProduct);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
        Add New Product
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="amazonUrl"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Amazon Product URL
          </label>
          <input
            type="text"
            id="amazonUrl"
            name="amazonUrl"
            value={state.amazonUrl}
            onChange={handleChange}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white ${
              state.errors.amazonUrl ? 'border-red-500' : ''
            }`}
            placeholder="https://www.amazon.com/dp/PRODUCT_ID"
          />
          {state.errors.amazonUrl && (
            <p className="mt-1 text-sm text-red-600">{state.errors.amazonUrl}</p>
          )}
        </div>

        <div>
          <label
            htmlFor="targetPrice"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Target Price ($)
          </label>
          <input
            type="number"
            id="targetPrice"
            name="targetPrice"
            value={state.targetPrice}
            onChange={handleChange}
            step="0.01"
            min="0"
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white ${
              state.errors.targetPrice ? 'border-red-500' : ''
            }`}
            placeholder="0.00"
          />
          {state.errors.targetPrice && (
            <p className="mt-1 text-sm text-red-600">{state.errors.targetPrice}</p>
          )}
        </div>

        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Email for Notifications
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={state.email}
            onChange={handleChange}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white ${
              state.errors.email ? 'border-red-500' : ''
            }`}
            placeholder="your@email.com"
          />
          {state.errors.email && (
            <p className="mt-1 text-sm text-red-600">{state.errors.email}</p>
          )}
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
        >
          Add Product
        </button>
      </form>
    </div>
  );
};

export default ProductInput; 