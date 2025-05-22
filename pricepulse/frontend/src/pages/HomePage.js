import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import ProductForm from '../components/products/ProductForm';
import ProductCard from '../components/products/ProductCard';
import Loader from '../components/common/Loader';
import EmptyState from '../components/common/EmptyState';
import { getAllProducts, checkApiHealth } from '../services/api';

const HomePage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkBackendAndFetchProducts();
  }, []);

  const checkBackendAndFetchProducts = async () => {
    setLoading(true);
    
    try {
      // First check if backend is running
      const healthCheck = await checkApiHealth();
      
      if (!healthCheck.success) {
        setError('Backend server is not running. Please make sure the backend is started and try again.');
        toast.error('Unable to connect to the backend server');
        setLoading(false);
        return;
      }
      
      // If health check passed, fetch products
      const response = await getAllProducts();
      if (response.success) {
        setProducts(response.products || []);
      } else {
        setError(response.error || 'Failed to fetch products');
        toast.error(response.error || 'Failed to fetch products');
      }
    } catch (err) {
      setError('Failed to fetch products. Please try again later.');
      toast.error('Failed to fetch products. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = () => {
    checkBackendAndFetchProducts();
  };

  const handleProductAdded = (newProduct) => {
    setProducts([newProduct, ...products]);
    toast.success('Product added successfully!');
  };

  return (
    <div className="home-page">
      <section className="mb-5">
        <ProductForm onProductAdded={handleProductAdded} />
      </section>

      <section>
        <h2 className="mb-4">Your Tracked Products</h2>
        
        {loading ? (
          <div className="centered-loader">
            <Loader />
          </div>
        ) : error ? (
          <div className="alert alert-danger" role="alert">
            <i className="fas fa-exclamation-circle me-2"></i>
            {error}
          </div>
        ) : products.length === 0 ? (
          <EmptyState 
            icon="fa-chart-line"
            title="No products tracked yet"
            message="Add an Amazon product URL above to start tracking prices!"
          />
        ) : (
          <div className="product-grid">
            {products.map(product => (
              <ProductCard 
                key={product.id} 
                product={product} 
                onRefresh={fetchProducts}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default HomePage;