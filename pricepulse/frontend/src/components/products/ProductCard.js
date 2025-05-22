import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { deleteProduct } from '../../services/api';
import Loader from '../common/Loader';

const ProductCard = ({ product, onRefresh }) => {
  const [loading, setLoading] = useState(false);

  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to stop tracking "${product.name}"?`)) {
      try {
        setLoading(true);
        const response = await deleteProduct(product.id);
        
        if (response.success) {
          toast.success('Product removed from tracking');
          if (onRefresh) {
            onRefresh();
          }
        } else {
          toast.error(response.error || 'Failed to remove product');
        }
      } catch (error) {
        toast.error('An error occurred. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  // Determine default image if product image is missing
  const productImage = product.image_url || 'https://via.placeholder.com/300x300?text=No+Image';

  return (
    <div className="card product-card">
      {loading && (
        <div className="card-img-overlay d-flex justify-content-center align-items-center bg-light bg-opacity-75">
          <Loader />
        </div>
      )}
      
      <img 
        src={productImage} 
        className="card-img-top product-image" 
        alt={product.name} 
      />
      
      <div className="card-body">
        <h5 className="card-title product-title">{product.name}</h5>
        
        <div className="d-flex justify-content-between align-items-center mb-3">
          <div>
            <span className="text-muted">Current Price:</span>
            <div className="price-current">₹{product.current_price || 'N/A'}</div>
          </div>
          
          <a 
            href={product.url} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="btn btn-sm btn-outline-primary"
          >
            <i className="fas fa-external-link-alt me-1"></i> View on Amazon
          </a>
        </div>
      </div>
      
      <div className="card-footer d-flex justify-content-between">
        <Link 
          to={`/product/${product.id}`} 
          className="btn btn-primary"
        >
          <i className="fas fa-chart-line me-1"></i> Price History
        </Link>
        
        <button 
          onClick={handleDelete} 
          className="btn btn-outline-danger"
          disabled={loading}
        >
          <i className="fas fa-trash-alt"></i>
        </button>
      </div>
    </div>
  );
};

export default ProductCard;