import React from 'react';

const EmptyState = ({ 
  icon = 'fa-search', 
  title = 'No results found', 
  message = 'Try changing your search or filters.',
  actionButton = null
}) => {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">
        <i className={`fas ${icon}`}></i>
      </div>
      <h3 className="mb-3">{title}</h3>
      <p className="text-muted mb-4">{message}</p>
      {actionButton && (
        <div className="mt-3">
          {actionButton}
        </div>
      )}
    </div>
  );
};

export default EmptyState;