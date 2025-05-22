import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { addProduct } from '../../services/api';
import Loader from '../common/Loader';

const ProductForm = ({ onProductAdded }) => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const validateUrl = (url) => {
    // Basic validation for Amazon URLs
    const amazonUrlPattern = /^https?:\/\/(www\.)?amazon\.(com|in)\/.*$/i;
    return amazonUrlPattern.test(url);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Reset error state
    setError(null);
    
    // Basic validation
    if (!url.trim()) {
      setError('Please enter a product URL');
      return;
    }
    
    if (!validateUrl(url)) {
      setError('Please enter a valid Amazon product URL');
      return;
    }
    
    try {
      setLoading(true);
      const response = await addProduct(url);
      
      if (response.success) {
        // Clear form and notify parent
        setUrl('');
        toast.success('Product added successfully!');
        if (onProductAdded && response.product) {
          onProductAdded(response.product);
        }
      } else {
        setError(response.error || 'Failed to add product');
        toast.error(response.error || 'Failed to add product');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
      toast.error('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="url-input-form">
      <h2 className="form-title">Track Amazon Product Prices</h2>
      <p className="text-muted mb-4">
        Enter an Amazon product URL to start tracking its price history and get notified about price drops.
      </p>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label htmlFor="productUrl" className="form-label">
            Amazon Product URL
          </label>
          <input
            type="url"
            className={`form-control ${error ? 'is-invalid' : ''}`}
            id="productUrl"
            placeholder="https://www.amazon.in/dp/B0CV7KZLL4/"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading}
            required
          />
          {error && <div className="invalid-feedback">{error}</div>}
          <div className="form-text">
            Example: https://www.amazon.in/dp/B0CV7KZLL4/
          </div>
        </div>
        
        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? (
            <>
              <Loader size="small" /> 
              <span className="ms-2">Adding Product...</span>
            </>
          ) : (
            <>
              <i className="fas fa-plus-circle me-2"></i>
              Start Tracking
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default ProductForm;