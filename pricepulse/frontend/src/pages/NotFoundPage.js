import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage = () => {
  return (
    <div className="text-center py-5">
      <div className="mb-4">
        <i className="fas fa-exclamation-triangle fa-5x text-warning"></i>
      </div>
      <h1 className="display-4 mb-3">404 - Page Not Found</h1>
      <p className="lead mb-4">
        The page you are looking for might have been removed, had its name changed, 
        or is temporarily unavailable.
      </p>
      <Link to="/" className="btn btn-primary btn-lg">
        <i className="fas fa-home me-2"></i> Back to Home
      </Link>
    </div>
  );
};

export default NotFoundPage;