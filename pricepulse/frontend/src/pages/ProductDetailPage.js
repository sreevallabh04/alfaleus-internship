import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import PriceChart from '../components/products/PriceChart';
import PriceAlertForm from '../components/products/PriceAlertForm';
import Loader from '../components/common/Loader';
import { getProduct, getPriceHistory } from '../services/api';

const ProductDetailPage = () => {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [priceHistory, setPriceHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProductData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch product details
      const productResponse = await getProduct(id);
      
      if (!productResponse.success) {
        setError(productResponse.error || 'Failed to fetch product details');
        toast.error(productResponse.error || 'Failed to fetch product details');
        return;
      }
      
      setProduct(productResponse.product);
      
      // Fetch price history
      const historyResponse = await getPriceHistory(id);
      
      if (historyResponse.success) {
        setPriceHistory(historyResponse.price_history || []);
      } else {
        toast.error('Failed to load price history');
      }
    } catch (err) {
      setError('An unexpected error occurred');
      toast.error('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchProductData();
  }, [fetchProductData]);

  // Calculate current price from price history
  const getCurrentPrice = () => {
    if (priceHistory && priceHistory.length > 0) {
      // Sort by timestamp descending to get the most recent price
      const sortedHistory = [...priceHistory].sort(
        (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
      );
      return sortedHistory[0].price;
    }
    return null;
  };

  const currentPrice = getCurrentPrice();

  if (loading) {
    return (
      <div className="text-center py-5">
        <Loader />
        <p className="mt-3">Loading product details...</p>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="alert alert-danger" role="alert">
        <h4 className="alert-heading">Error!</h4>
        <p>{error || 'Product not found'}</p>
        <hr />
        <Link to="/" className="btn btn-primary">
          <i className="fas fa-arrow-left me-2"></i> Back to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="product-detail-page">
      <div className="mb-4">
        <Link to="/" className="btn btn-outline-secondary">
          <i className="fas fa-arrow-left me-2"></i> Back to all products
        </Link>
      </div>
      
      <div className="row">
        <div className="col-md-4 mb-4">
          <div className="card">
            <img 
              src={product.image_url || 'https://via.placeholder.com/300x300?text=No+Image'} 
              className="card-img-top product-image" 
              alt={product.name}
              style={{ maxHeight: '300px', objectFit: 'contain', padding: '20px' }}
            />
            <div className="card-body">
              <h1 className="card-title h4">{product.name}</h1>
              
              {currentPrice && (
                <div className="mt-3">
                  <div className="price-current mb-1">₹{currentPrice.toFixed(2)}</div>
                  <div className="text-muted small">
                    Last updated: {new Date(product.updated_at).toLocaleString()}
                  </div>
                </div>
              )}
              
              <div className="mt-3">
                <a 
                  href={product.url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="btn btn-primary"
                >
                  <i className="fas fa-external-link-alt me-2"></i> View on Amazon
                </a>
              </div>
            </div>
          </div>
        </div>
        
        <div className="col-md-8">
          <div className="card mb-4">
            <div className="card-body">
              <PriceChart 
                priceHistory={priceHistory} 
                title={`Price History for ${product.name}`} 
              />
            </div>
          </div>
          
          <PriceAlertForm 
            productId={product.id}
            currentPrice={currentPrice}
          />
        </div>
      </div>
      
      {/* Future enhancement: Platform Comparison */}
      <div className="mt-5">
        <h3 className="mb-4">
          <i className="fas fa-store me-2"></i> Price Comparison
        </h3>
        <div className="card">
          <div className="card-body text-center py-5">
            <i className="fas fa-code text-muted fa-3x mb-3"></i>
            <h4>Platform Comparison Coming Soon</h4>
            <p className="text-muted">
              We're working on comparing prices across multiple platforms like Flipkart, Meesho, and more.
              Check back soon!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailPage;