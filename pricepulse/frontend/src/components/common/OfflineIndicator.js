import React, { useState, useEffect } from 'react';
import { Alert, Button } from 'react-bootstrap';
import { isOfflineMode, setOfflineMode, checkApiHealth } from '../../services/api';

/**
 * Component that shows a banner when the application is in offline mode
 * Provides controls to retry connection or explicitly toggle offline mode
 */
const OfflineIndicator = () => {
  const [offlineState, setOfflineState] = useState(isOfflineMode());
  const [isRetrying, setIsRetrying] = useState(false);

  // Listen for offline mode changes from other components
  useEffect(() => {
    const handleOfflineModeChange = (event) => {
      setOfflineState(event.detail.enabled);
    };

    window.addEventListener('offlinemodechange', handleOfflineModeChange);
    
    // Initial check
    setOfflineState(isOfflineMode());
    
    return () => {
      window.removeEventListener('offlinemodechange', handleOfflineModeChange);
    };
  }, []);

  // Don't render anything if we're not in offline mode
  if (!offlineState) {
    return null;
  }

  // Handler to retry connecting to the backend
  const handleRetryConnection = async () => {
    setIsRetrying(true);
    
    try {
      const healthResult = await checkApiHealth(3, 800);
      
      if (healthResult.success && !healthResult.offline) {
        // Backend is available, switch back to online mode
        setOfflineMode(false);
        setOfflineState(false);
      }
    } catch (error) {
      console.error('Error retrying connection:', error);
    } finally {
      setIsRetrying(false);
    }
  };

  // Handler to toggle offline mode manually
  const handleToggleOfflineMode = () => {
    const newState = !offlineState;
    setOfflineMode(newState);
    setOfflineState(newState);
  };

  return (
    <Alert 
      variant="warning" 
      className="mb-0 rounded-0 text-center d-flex justify-content-between align-items-center"
    >
      <div className="d-flex align-items-center">
        <i className="fas fa-wifi-slash me-2"></i>
        <span><strong>Offline Mode</strong> - Using cached data</span>
      </div>
      
      <div>
        <Button
          variant="outline-primary"
          size="sm"
          className="me-2"
          onClick={handleRetryConnection}
          disabled={isRetrying}
        >
          {isRetrying ? (
            <>
              <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
              Connecting...
            </>
          ) : (
            <>
              <i className="fas fa-sync-alt me-1"></i> Retry Connection
            </>
          )}
        </Button>
        
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={handleToggleOfflineMode}
        >
          <i className="fas fa-power-off me-1"></i> 
          {offlineState ? 'Exit Offline Mode' : 'Enter Offline Mode'}
        </Button>
      </div>
    </Alert>
  );
};

export default OfflineIndicator;