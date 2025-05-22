import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { motion, AnimatePresence } from 'framer-motion';
import { deleteProduct } from '../../services/api';
import Loader from '../common/Loader';

// Animation variants
const cardVariants = {
  hidden: { 
    opacity: 0, 
    y: 30, 
    scale: 0.9 
  },
  visible: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: {
      type: 'spring',
      stiffness: 100,
      damping: 15,
      mass: 1,
      delayChildren: 0.2,
      staggerChildren: 0.1
    }
  },
  hover: { 
    y: -10,
    scale: 1.02,
    boxShadow: "0 10px 25px rgba(0,0,0,0.1)",
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 15
    }
  },
  tap: { 
    scale: 0.98,
    boxShadow: "0 5px 10px rgba(0,0,0,0.1)",
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 20
    }
  }
};

const contentVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 200,
      damping: 20
    }
  }
};

const buttonVariants = {
  initial: { scale: 1 },
  hover: { 
    scale: 1.05,
    boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 10
    }
  },
  tap: { scale: 0.95 }
};

const ProductCard = ({ product, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [isImageLoaded, setIsImageLoaded] = useState(false);

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

  const handleImageLoad = () => {
    setIsImageLoaded(true);
  };

  return (
    <motion.div 
      className="card product-card"
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      whileTap="tap"
      layout
    >
      <AnimatePresence>
        {loading && (
          <motion.div 
            className="card-img-overlay d-flex justify-content-center align-items-center"
            style={{ 
              background: "rgba(255, 255, 255, 0.8)",
              backdropFilter: "blur(4px)" 
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ 
                scale: 1, 
                opacity: 1,
                transition: {
                  type: 'spring',
                  stiffness: 200,
                  damping: 20
                }
              }}
              exit={{ 
                scale: 0.5, 
                opacity: 0,
                transition: { duration: 0.2 }
              }}
            >
              <Loader />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      
      <motion.div
        className="image-container"
        initial={{ opacity: 0 }}
        animate={{ 
          opacity: isImageLoaded ? 1 : 0,
          transition: { duration: 0.5 }
        }}
      >
        <motion.img 
          src={productImage} 
          className="card-img-top product-image" 
          alt={product.name}
          onLoad={handleImageLoad}
          whileHover={{ 
            scale: 1.05,
            transition: { duration: 0.3 }
          }}
        />
      </motion.div>
      
      <motion.div 
        className="card-body"
        variants={contentVariants}
      >
        <motion.h5 
          className="card-title product-title"
          variants={contentVariants}
        >
          {product.name}
        </motion.h5>
        
        <motion.div 
          className="d-flex justify-content-between align-items-center mb-3"
          variants={contentVariants}
        >
          <div>
            <span className="text-muted">Current Price:</span>
            <motion.div 
              className="price-current"
              initial={{ color: "#212529" }}
              animate={{ 
                color: product.price_changed ? "#dc3545" : "#212529",
                transition: { duration: 0.5 }
              }}
            >
              ₹{product.current_price || 'N/A'}
            </motion.div>
          </div>
          
          <motion.a 
            href={product.url} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="btn btn-sm btn-outline-primary"
            variants={buttonVariants}
            whileHover="hover"
            whileTap="tap"
          >
            <i className="fas fa-external-link-alt me-1"></i> View on Amazon
          </motion.a>
        </motion.div>
      </motion.div>
      
      <motion.div 
        className="card-footer d-flex justify-content-between"
        variants={contentVariants}
      >
        <motion.div
          variants={buttonVariants}
          whileHover="hover"
          whileTap="tap"
        >
          <Link 
            to={`/product/${product.id}`} 
            className="btn btn-primary"
          >
            <i className="fas fa-chart-line me-1"></i> Price History
          </Link>
        </motion.div>
        
        <motion.button 
          onClick={handleDelete} 
          className="btn btn-outline-danger"
          disabled={loading}
          variants={buttonVariants}
          whileHover="hover"
          whileTap="tap"
        >
          <i className="fas fa-trash-alt"></i>
        </motion.button>
      </motion.div>

      <style jsx="true">{`
        .product-card {
          height: 100%;
          display: flex;
          flex-direction: column;
          border-radius: 12px;
          overflow: hidden;
          transition: all 0.3s ease;
          border: none;
          box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .image-container {
          overflow: hidden;
          height: 200px;
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: #f8f9fa;
        }
        
        .product-image {
          width: 100%;
          height: 100%;
          object-fit: contain;
          padding: 10px;
        }
        
        .product-title {
          font-size: 1.1rem;
          font-weight: 600;
          margin-bottom: 1rem;
          height: 2.4rem;
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
        }
        
        .price-current {
          font-size: 1.3rem;
          font-weight: bold;
        }
        
        .card-body {
          flex: 1;
        }
      `}</style>
    </motion.div>
  );
};

export default ProductCard;