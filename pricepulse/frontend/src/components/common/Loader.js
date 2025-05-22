import React from 'react';

const Loader = ({ size = 'medium' }) => {
  let spinnerSize;
  
  switch (size) {
    case 'small':
      spinnerSize = '1rem';
      break;
    case 'large':
      spinnerSize = '3rem';
      break;
    case 'medium':
    default:
      spinnerSize = '2rem';
  }
  
  return (
    <div 
      className="loading-spinner" 
      style={{ 
        width: spinnerSize, 
        height: spinnerSize,
        borderWidth: `calc(${spinnerSize} / 8)`
      }}
      role="status"
      aria-label="Loading"
    >
      <span className="visually-hidden">Loading...</span>
    </div>
  );
};

export default Loader;