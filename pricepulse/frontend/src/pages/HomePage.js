import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-toastify';
import { motion, AnimatePresence } from 'framer-motion';
import ProductForm from '../components/products/ProductForm';
import ProductCard from '../components/products/ProductCard';
import Loader from '../components/common/Loader';
import EmptyState from '../components/common/EmptyState';
import { getAllProducts, checkApiHealth } from '../services/api';

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: { 
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: { 
    y: 0, 
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 100,
      damping: 10
    }
  }
};

const errorVariants = {
  hidden: { scale: 0.8, opacity: 0 },
  visible: { 
    scale: 1, 
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 200,
      damping: 15
    }
  },
  exit: {
    scale: 0.8,
    opacity: 0
  }
};

const HomePage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retrying, setRetrying] = useState(false);
  const [serverStatus, setServerStatus] = useState('unknown'); // 'online', 'offline', 'unknown'

  // Memoize functions used in useEffect to avoid dependency warnings
  const performHealthCheck = useCallback(async (silent = true) => {
    try {
      const healthCheck = await checkApiHealth();
      const newStatus = healthCheck.success ? 'online' : 'offline';
      
      // Only notify on status change
      if (serverStatus !== newStatus) {
        setServerStatus(newStatus);
        if (!silent) {
          if (newStatus === 'online') {
            toast.success('Connected to backend server');
          } else {
            toast.error('Lost connection to backend server');
          }
        }
      }
      
      return healthCheck;
    } catch (err) {
      setServerStatus('offline');
      return { success: false, error: err.message };
    }
  }, [serverStatus]);

  const checkBackendAndFetchProducts = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // First check if backend is running
      const healthCheck = await performHealthCheck(false);
      
      if (!healthCheck.success) {
        setError('Backend server is not running. Please make sure the backend is started and try again.');
        setLoading(false);
        return;
      }
      
      // If health check passed, fetch products
      const response = await getAllProducts();
      if (response.success) {
        // Animate products in with a slight delay
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
      setRetrying(false);
    }
  }, [performHealthCheck]);
  
  useEffect(() => {
    checkBackendAndFetchProducts();
    
    // Setup periodic server health check
    const healthCheckInterval = setInterval(() => {
      performHealthCheck();
    }, 30000); // Check every 30 seconds
    
    return () => clearInterval(healthCheckInterval);
  }, [checkBackendAndFetchProducts, performHealthCheck]);

  const handleRetry = () => {
    setRetrying(true);
    setTimeout(() => {
      checkBackendAndFetchProducts();
    }, 800); // Short delay for animation
  };

  const fetchProducts = () => {
    checkBackendAndFetchProducts();
  };

  const handleProductAdded = (newProduct) => {
    setProducts(prevProducts => [newProduct, ...prevProducts]);
    toast.success('Product added successfully!');
  };

  return (
    <motion.div 
      className="home-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Server Status Indicator */}
      <motion.div 
        className={`server-status ${serverStatus}`}
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <div className="status-indicator">
          <span className={`status-dot ${serverStatus}`}></span>
          <span className="status-text">
            {serverStatus === 'online' ? 'Connected to Server' : 
             serverStatus === 'offline' ? 'Server Offline' : 'Checking Server Status...'}
          </span>
        </div>
      </motion.div>

      <motion.section 
        className="mb-5"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        <ProductForm onProductAdded={handleProductAdded} />
      </motion.section>

      <motion.section
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <motion.h2 
          className="mb-4"
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.3, type: 'spring' }}
        >
          Your Tracked Products
        </motion.h2>
        
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div 
              key="loader"
              className="centered-loader"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <Loader />
            </motion.div>
          ) : error ? (
            <motion.div 
              key="error"
              className="alert alert-danger" 
              role="alert"
              variants={errorVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              layoutId="statusContent"
            >
              <i className="fas fa-exclamation-circle me-2"></i>
              {error}
              <motion.div className="mt-3">
                <motion.button 
                  className="btn btn-outline-primary"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleRetry}
                  disabled={retrying}
                >
                  {retrying ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Retrying...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-sync-alt me-2"></i>
                      Retry Connection
                    </>
                  )}
                </motion.button>
              </motion.div>
            </motion.div>
          ) : products.length === 0 ? (
            <motion.div
              key="empty"
              variants={errorVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              layoutId="statusContent"
            >
              <EmptyState 
                icon="fa-chart-line"
                title="No products tracked yet"
                message="Add an Amazon product URL above to start tracking prices!"
              />
            </motion.div>
          ) : (
            <motion.div 
              key="products"
              className="product-grid"
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              layoutId="statusContent"
            >
              {products.map((product, index) => (
                <motion.div
                  key={product.id}
                  variants={itemVariants}
                  custom={index}
                  layout
                >
                  <ProductCard 
                    product={product} 
                    onRefresh={fetchProducts}
                  />
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.section>

      <style jsx="true">{`
        .server-status {
          display: flex;
          justify-content: flex-end;
          margin-bottom: 1rem;
        }
        .status-indicator {
          display: flex;
          align-items: center;
          padding: 0.5rem 1rem;
          border-radius: 2rem;
          background-color: #f8f9fa;
          box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .status-dot {
          height: 10px;
          width: 10px;
          border-radius: 50%;
          margin-right: 8px;
        }
        .status-dot.online {
          background-color: #28a745;
          box-shadow: 0 0 5px #28a745;
        }
        .status-dot.offline {
          background-color: #dc3545;
          box-shadow: 0 0 5px #dc3545;
        }
        .status-dot.unknown {
          background-color: #ffc107;
          box-shadow: 0 0 5px #ffc107;
        }
        .centered-loader {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 200px;
        }
        .product-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1.5rem;
        }
      `}</style>
    </motion.div>
  );
};

export default HomePage;