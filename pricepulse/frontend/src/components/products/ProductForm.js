import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { motion, AnimatePresence } from 'framer-motion';
import { addProduct } from '../../services/api';
import Loader from '../common/Loader';

// Animation variants
const formContainerVariants = {
  hidden: { opacity: 0, y: -20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 100,
      damping: 15,
      staggerChildren: 0.1
    }
  }
};

const formItemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 100,
      damping: 10
    }
  }
};

const buttonVariants = {
  initial: { scale: 1 },
  hover: { 
    scale: 1.05,
    boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
    backgroundColor: "#0056b3",
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 10
    }
  },
  tap: { scale: 0.95 }
};

const errorVariants = {
  hidden: { 
    opacity: 0, 
    height: 0, 
    y: -10 
  },
  visible: {
    opacity: 1,
    height: 'auto',
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 200,
      damping: 20
    }
  },
  exit: {
    opacity: 0,
    height: 0,
    y: -10,
    transition: {
      duration: 0.2
    }
  }
};

const ProductForm = ({ onProductAdded }) => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const validateUrl = (url) => {
    // Basic validation for Amazon URLs
    const amazonUrlPattern = /^https?:\/\/(www\.)?amazon\.(com|in)\/.*$/i;
    return amazonUrlPattern.test(url);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Reset states
    setError(null);
    setSuccess(false);
    
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
        setSuccess(true);
        
        // Reset success state after 3 seconds
        setTimeout(() => setSuccess(false), 3000);
        
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
    <motion.div 
      className="url-input-form"
      variants={formContainerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.h2 
        className="form-title"
        variants={formItemVariants}
      >
        Track Amazon Product Prices
      </motion.h2>
      
      <motion.p 
        className="text-muted mb-4"
        variants={formItemVariants}
      >
        Enter an Amazon product URL to start tracking its price history and get notified about price drops.
      </motion.p>
      
      <motion.form 
        onSubmit={handleSubmit}
        variants={formItemVariants}
      >
        <motion.div 
          className="mb-3"
          variants={formItemVariants}
        >
          <motion.label 
            htmlFor="productUrl" 
            className="form-label"
            variants={formItemVariants}
          >
            Amazon Product URL
          </motion.label>
          
          <motion.div
            initial={{ boxShadow: "0 0 0 rgba(13,110,253,0)" }}
            whileFocus={{ boxShadow: "0 0 0 0.25rem rgba(13,110,253,0.25)" }}
            transition={{ duration: 0.3 }}
          >
            <motion.input
              type="url"
              className={`form-control ${error ? 'is-invalid' : ''} ${success ? 'is-valid' : ''}`}
              id="productUrl"
              placeholder="https://www.amazon.in/dp/B0CV7KZLL4/"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={loading}
              required
              whileFocus={{ scale: 1.01 }}
              transition={{ duration: 0.2 }}
            />
          </motion.div>
          
          <AnimatePresence mode="wait">
            {error && (
              <motion.div 
                className="invalid-feedback"
                variants={errorVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>
          
          <motion.div 
            className="form-text"
            variants={formItemVariants}
          >
            Example: https://www.amazon.in/dp/B0CV7KZLL4/
          </motion.div>
        </motion.div>
        
        <motion.button 
          type="submit" 
          className={`btn btn-primary ${success ? 'btn-success' : ''}`}
          disabled={loading}
          variants={buttonVariants}
          initial="initial"
          whileHover="hover"
          whileTap="tap"
          animate={success ? { 
            backgroundColor: "#28a745",
            transition: { duration: 0.3 }
          } : {}}
        >
          {loading ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="d-flex align-items-center"
            >
              <motion.div
                initial={{ rotate: 0 }}
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
              >
                <Loader size="small" /> 
              </motion.div>
              <motion.span 
                className="ms-2"
                initial={{ opacity: 0, x: -5 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                Adding Product...
              </motion.span>
            </motion.div>
          ) : success ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="d-flex align-items-center"
            >
              <motion.i 
                className="fas fa-check-circle me-2"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200 }}
              />
              <span>Product Added!</span>
            </motion.div>
          ) : (
            <>
              <motion.i 
                className="fas fa-plus-circle me-2"
                initial={{ rotate: 0 }}
                animate={{ rotate: [0, 15, 0, -15, 0] }}
                transition={{ duration: 1, repeat: Infinity, repeatDelay: 5 }}
              />
              <span>Start Tracking</span>
            </>
          )}
        </motion.button>
      </motion.form>
      
      <style jsx="true">{`
        .url-input-form {
          background-color: #fff;
          border-radius: 12px;
          padding: 2rem;
          box-shadow: 0 5px 20px rgba(0,0,0,0.08);
          margin-bottom: 2rem;
        }
        
        .form-title {
          font-weight: 700;
          margin-bottom: 0.5rem;
          background: linear-gradient(45deg, #0d6efd, #0dcaf0);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        
        .form-control:focus {
          border-color: #0d6efd;
          box-shadow: 0 0 0 0.25rem rgba(13,110,253,0.25);
        }
        
        .form-control.is-valid {
          border-color: #28a745;
          padding-right: calc(1.5em + 0.75rem);
          background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8'%3e%3cpath fill='%2328a745' d='M2.3 6.73L.6 4.53c-.4-1.04.46-1.4 1.1-.8l1.1 1.4 3.4-3.8c.6-.63 1.6-.27 1.2.7l-4 4.6c-.43.5-.8.4-1.1.1z'/%3e%3c/svg%3e");
          background-repeat: no-repeat;
          background-position: right calc(0.375em + 0.1875rem) center;
          background-size: calc(0.75em + 0.375rem) calc(0.75em + 0.375rem);
        }
        
        .btn-primary {
          transition: all 0.3s ease;
        }
      `}</style>
    </motion.div>
  );
};

export default ProductForm;