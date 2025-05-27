import { useEffect } from 'react';
import { ThemeProvider, useThemeContext } from './context/ThemeContext';
import Header from './components/Header';
import ProductList from './components/ProductList';
import ProductInput from './components/ProductInput';
import PriceTrendGraph from './components/PriceTrendGraph';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorBoundary from './components/ErrorBoundary';
import Footer from './components/Footer';
import { useProducts } from './hooks/useProducts';

const AppContent: React.FC = () => {
  const { isDarkMode, toggleTheme } = useThemeContext();
  const {
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
  } = useProducts();

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header onThemeToggle={toggleTheme} isDarkMode={isDarkMode} />
      <main className="container mx-auto px-4 py-8 mt-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <ProductInput onAddProduct={handleAddProduct} />
            {error && (
              <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}
            {isLoading ? (
              <div className="mt-8 flex justify-center">
                <LoadingSpinner size="lg" />
              </div>
            ) : (
              <ProductList
                products={products}
                onDeleteProduct={handleDeleteProduct}
                onSelectProduct={handleSelectProduct}
                selectedProductId={selectedProduct?.id}
              />
            )}
          </div>
          <div>
            {selectedProduct && (
              <div className="space-y-6">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                      {selectedProduct.title}
                    </h2>
                    <button
                      onClick={handleRefreshData}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                      disabled={isRefreshing}
                    >
                      {isRefreshing ? (
                        <LoadingSpinner size="sm" />
                      ) : (
                        'Refresh Data'
                      )}
                    </button>
                  </div>
                  <div className="mb-6">
                    <img
                      src={selectedProduct.image_url}
                      alt={selectedProduct.title}
                      className="w-full h-64 object-contain rounded-lg"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                      <p className="text-sm text-gray-600 dark:text-gray-300">Current Price</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        ${selectedProduct.current_price.toFixed(2)}
                      </p>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                      <p className="text-sm text-gray-600 dark:text-gray-300">Target Price</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        ${selectedProduct.target_price.toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>
                <PriceTrendGraph
                  priceHistory={selectedProduct.priceHistory}
                  currentPrice={selectedProduct.current_price}
                  targetPrice={selectedProduct.target_price}
                />
              </div>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </ErrorBoundary>
  );
};

export default App;
