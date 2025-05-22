import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { createPriceAlert } from '../../services/api';
import Loader from '../common/Loader';

const PriceAlertForm = ({ productId, currentPrice }) => {
  const [email, setEmail] = useState('');
  const [targetPrice, setTargetPrice] = useState(
    currentPrice ? (currentPrice * 0.9).toFixed(2) : '' // Default to 10% below current price
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Reset states
    setError(null);
    setSuccess(false);
    
    // Validate email
    if (!validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }
    
    // Validate target price
    const targetPriceFloat = parseFloat(targetPrice);
    if (isNaN(targetPriceFloat) || targetPriceFloat <= 0) {
      setError('Please enter a valid target price');
      return;
    }
    
    try {
      setLoading(true);
      const response = await createPriceAlert(productId, email, targetPriceFloat);
      
      if (response.success) {
        setSuccess(true);
        toast.success('Price alert set successfully!');
      } else {
        setError(response.error || 'Failed to set price alert');
        toast.error(response.error || 'Failed to set price alert');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
      toast.error('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="alert-form">
      <h4 className="mb-3">
        <i className="fas fa-bell me-2"></i> Price Drop Alert
      </h4>
      
      {success ? (
        <div className="alert alert-success">
          <i className="fas fa-check-circle me-2"></i>
          Alert set! We'll email you at <strong>{email}</strong> when the price drops below ₹{targetPrice}.
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <p className="text-muted mb-3">
            Get notified when the price drops below your target price.
          </p>
          
          <div className="mb-3">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              type="email"
              className={`form-control ${error && !validateEmail(email) ? 'is-invalid' : ''}`}
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              disabled={loading}
            />
          </div>
          
          <div className="mb-3">
            <label htmlFor="targetPrice" className="form-label">
              Target Price (₹)
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              className={`form-control ${error && !targetPrice ? 'is-invalid' : ''}`}
              id="targetPrice"
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              placeholder="Enter your desired price"
              required
              disabled={loading}
            />
            {currentPrice && (
              <div className="form-text">
                Current price: ₹{currentPrice.toFixed(2)}
              </div>
            )}
          </div>
          
          {error && (
            <div className="alert alert-danger">
              <i className="fas fa-exclamation-circle me-2"></i>
              {error}
            </div>
          )}
          
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader size="small" /> 
                <span className="ms-2">Setting Alert...</span>
              </>
            ) : (
              <>
                <i className="fas fa-bell me-2"></i>
                Notify Me
              </>
            )}
          </button>
        </form>
      )}
    </div>
  );
};

export default PriceAlertForm;