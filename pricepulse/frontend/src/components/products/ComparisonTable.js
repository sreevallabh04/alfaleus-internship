import React, { useState } from 'react';
import { Button, Spinner, Alert } from 'react-bootstrap';

/**
 * Displays a comparison table of prices across different platforms
 * 
 * @param {Object} props
 * @param {Object} props.comparisonData - Data from the comparison API
 * @param {boolean} props.loading - Whether comparison data is being loaded
 * @param {string} props.error - Error message if comparison failed
 * @param {Function} props.onRetry - Function to call when retry button is clicked
 */
const ComparisonTable = ({ comparisonData, loading, error, onRetry }) => {
  const [showAll, setShowAll] = useState(false);

  // If loading, show spinner
  if (loading) {
    return (
      <div className="text-center py-4">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3">Looking for the best prices across platforms...</p>
      </div>
    );
  }

  // If error, show error message with retry button
  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Comparison Failed</Alert.Heading>
        <p>{error}</p>
        <div className="d-flex justify-content-end">
          <Button onClick={onRetry} variant="outline-danger">
            <i className="fas fa-sync-alt me-2"></i> Retry Comparison
          </Button>
        </div>
      </Alert>
    );
  }

  // If no data, show message
  if (!comparisonData || !comparisonData.comparison) {
    return (
      <Alert variant="info">
        <p className="mb-0">No comparison data available. The system is still gathering data from other platforms.</p>
      </Alert>
    );
  }

  // Process the comparison data
  const { original_product, comparison } = comparisonData;
  const originalPlatform = original_product.platform || 'Amazon';
  
  // Get all Amazon products
  const amazonProducts = comparison.amazon || [];
  
  // Get all Flipkart products
  const flipkartProducts = comparison.flipkart || [];

  // Total number of products
  const totalProducts = amazonProducts.length + flipkartProducts.length;
  
  // Get up to 3 products for initial display
  const limitedAmazon = showAll ? amazonProducts : amazonProducts.slice(0, 2);
  const limitedFlipkart = showAll ? flipkartProducts : flipkartProducts.slice(0, 2);
  
  // Check if we have more products to show
  const hasMoreProducts = !showAll && totalProducts > 4;

  // Format price with currency
  const formatPrice = (price, currency = '₹') => {
    if (!price && price !== 0) return 'N/A';
    return `${currency}${parseFloat(price).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
  };

  // Determine if a price is the lowest
  const getLowestPrice = () => {
    let allPrices = [];
    
    // Add original product price
    if (original_product.price) {
      allPrices.push(original_product.price);
    }
    
    // Add Amazon prices
    amazonProducts.forEach(product => {
      if (product.price) {
        allPrices.push(product.price);
      }
    });
    
    // Add Flipkart prices
    flipkartProducts.forEach(product => {
      if (product.price) {
        allPrices.push(product.price);
      }
    });
    
    // Return the lowest price
    return Math.min(...allPrices);
  };
  
  const lowestPrice = getLowestPrice();

  return (
    <div className="comparison-table">
      <h3 className="mb-3">
        <i className="fas fa-store me-2"></i> Price Comparison
      </h3>
      
      <div className="table-responsive">
        <table className="table table-bordered">
          <thead className="table-light">
            <tr>
              <th style={{ width: '20%' }}>Platform</th>
              <th style={{ width: '40%' }}>Product</th>
              <th style={{ width: '15%' }}>Price</th>
              <th style={{ width: '15%' }}>Rating</th>
              <th style={{ width: '10%' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {/* Original product */}
            <tr className="table-primary bg-opacity-25">
              <td>
                <strong>{originalPlatform}</strong>
                <div className="small">(Current)</div>
              </td>
              <td>
                <div className="d-flex align-items-center">
                  {original_product.image_url && (
                    <img 
                      src={original_product.image_url} 
                      alt={original_product.name}
                      className="me-2"
                      style={{ maxWidth: '50px', maxHeight: '50px' }}
                    />
                  )}
                  <div>{original_product.name}</div>
                </div>
              </td>
              <td className={original_product.price === lowestPrice ? 'text-success fw-bold' : ''}>
                {formatPrice(original_product.price)}
              </td>
              <td>
                {original_product.rating ? (
                  <div>{original_product.rating} <i className="fas fa-star text-warning"></i></div>
                ) : (
                  <span className="text-muted">N/A</span>
                )}
              </td>
              <td>
                <a 
                  href={original_product.url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="btn btn-sm btn-primary"
                >
                  View
                </a>
              </td>
            </tr>
            
            {/* Flipkart products */}
            {limitedFlipkart.length > 0 && limitedFlipkart.map((product, index) => (
              <tr key={`flipkart-${index}`}>
                <td>
                  <div className="text-info">Flipkart</div>
                </td>
                <td>
                  <div className="d-flex align-items-center">
                    {product.image_url && (
                      <img 
                        src={product.image_url} 
                        alt={product.name}
                        className="me-2"
                        style={{ maxWidth: '50px', maxHeight: '50px' }}
                      />
                    )}
                    <div>{product.name}</div>
                  </div>
                </td>
                <td className={product.price === lowestPrice ? 'text-success fw-bold' : ''}>
                  {formatPrice(product.price)}
                </td>
                <td>
                  {product.rating ? (
                    <div>{product.rating} <i className="fas fa-star text-warning"></i></div>
                  ) : (
                    <span className="text-muted">N/A</span>
                  )}
                </td>
                <td>
                  <a 
                    href={product.url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="btn btn-sm btn-primary"
                  >
                    View
                  </a>
                </td>
              </tr>
            ))}
            
            {/* Amazon products (excluding the original if it's from Amazon) */}
            {limitedAmazon.length > 0 && limitedAmazon.map((product, index) => (
              <tr key={`amazon-${index}`}>
                <td>
                  <div className="text-warning">Amazon</div>
                </td>
                <td>
                  <div className="d-flex align-items-center">
                    {product.image_url && (
                      <img 
                        src={product.image_url} 
                        alt={product.name}
                        className="me-2"
                        style={{ maxWidth: '50px', maxHeight: '50px' }}
                      />
                    )}
                    <div>{product.name}</div>
                  </div>
                </td>
                <td className={product.price === lowestPrice ? 'text-success fw-bold' : ''}>
                  {formatPrice(product.price)}
                </td>
                <td>
                  {product.rating ? (
                    <div>{product.rating} <i className="fas fa-star text-warning"></i></div>
                  ) : (
                    <span className="text-muted">N/A</span>
                  )}
                </td>
                <td>
                  <a 
                    href={product.url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="btn btn-sm btn-primary"
                  >
                    View
                  </a>
                </td>
              </tr>
            ))}
            
            {/* Show more button if there are more products */}
            {hasMoreProducts && (
              <tr className="table-light">
                <td colSpan="5" className="text-center">
                  <Button 
                    variant="link" 
                    onClick={() => setShowAll(true)}
                    className="text-decoration-none"
                  >
                    <i className="fas fa-plus-circle me-2"></i>
                    Show {totalProducts - 4} More Options
                  </Button>
                </td>
              </tr>
            )}
            
            {/* Show less button if showing all */}
            {showAll && totalProducts > 4 && (
              <tr className="table-light">
                <td colSpan="5" className="text-center">
                  <Button 
                    variant="link" 
                    onClick={() => setShowAll(false)}
                    className="text-decoration-none"
                  >
                    <i className="fas fa-minus-circle me-2"></i>
                    Show Less
                  </Button>
                </td>
              </tr>
            )}
            
            {/* If no alternative products found */}
            {totalProducts === 0 && (
              <tr>
                <td colSpan="5" className="text-center py-4">
                  <div className="text-muted">
                    <i className="fas fa-search me-2"></i>
                    No alternative products found across platforms
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      <div className="mt-3 small text-muted">
        <i className="fas fa-info-circle me-2"></i>
        Prices and availability may vary. The green highlighted price indicates the lowest price available.
      </div>
    </div>
  );
};

export default ComparisonTable;