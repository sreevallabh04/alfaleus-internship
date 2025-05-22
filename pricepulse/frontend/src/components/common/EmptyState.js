import React from 'react';
import { motion } from 'framer-motion';

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      delay: 0.3,
      when: "beforeChildren",
      staggerChildren: 0.2
    }
  }
};

const iconVariants = {
  hidden: { 
    scale: 0.6,
    opacity: 0,
    y: -20
  },
  visible: { 
    scale: 1,
    opacity: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 200,
      damping: 10
    }
  }
};

const textVariants = {
  hidden: { 
    opacity: 0,
    y: 20
  },
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
  hidden: { 
    opacity: 0,
    scale: 0.8
  },
  visible: { 
    opacity: 1,
    scale: 1,
    transition: {
      type: 'spring',
      stiffness: 200,
      damping: 10,
      delay: 0.6
    }
  },
  hover: {
    scale: 1.05,
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 10
    }
  },
  tap: {
    scale: 0.95
  }
};

const EmptyState = ({ 
  icon = 'fa-search', 
  title = 'No results found', 
  message = 'Try changing your search or filters.',
  actionButton = null
}) => {
  return (
    <motion.div 
      className="empty-state"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div 
        className="empty-state-icon"
        variants={iconVariants}
        animate={{
          scale: [1, 1.1, 1],
          opacity: [1, 0.8, 1]
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          repeatType: "reverse"
        }}
      >
        <motion.i 
          className={`fas ${icon}`}
          animate={{
            rotate: icon === 'fa-search' ? [0, -10, 10, -10, 0] : 0
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            repeatDelay: 3
          }}
        ></motion.i>
      </motion.div>
      
      <motion.h3 
        className="mb-3"
        variants={textVariants}
      >
        {title}
      </motion.h3>
      
      <motion.p 
        className="text-muted mb-4"
        variants={textVariants}
      >
        {message}
      </motion.p>
      
      {actionButton && (
        <motion.div 
          className="mt-3"
          variants={buttonVariants}
          whileHover="hover"
          whileTap="tap"
        >
          {actionButton}
        </motion.div>
      )}
      
      <style jsx="true">{`
        .empty-state {
          text-align: center;
          padding: 3rem 1.5rem;
          background-color: #f8f9fa;
          border-radius: 12px;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        
        .empty-state-icon {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          background: linear-gradient(135deg, #4dabf7, #0d6efd);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2rem;
          margin: 0 auto 1.5rem;
          box-shadow: 0 8px 20px rgba(13, 110, 253, 0.3);
        }
      `}</style>
    </motion.div>
  );
};

export default EmptyState;