import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import { Button } from 'react-bootstrap';
import Navbar from './components/layout/Navbar';
import HomePage from './pages/HomePage';
import ProductDetailPage from './pages/ProductDetailPage';
import NotFoundPage from './pages/NotFoundPage';
import OfflineIndicator from './components/common/OfflineIndicator';
import { checkApiHealth, isOfflineMode, setOfflineMode } from './services/api';
import './App.css';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  const [backendStatus, setBackendStatus] = useState('checking');

  // Function to check backend health
  const checkBackendServer = async (showToastOnError = true) => {
    try {
      // If already in offline mode (user explicitly chose it), don't show error
      if (isOfflineMode()) {
        setBackendStatus('offline');
        return false;
      }
      
      setBackendStatus('checking');
      // Attempt to check API health with more generous parameters
      const healthResult = await checkApiHealth(8, 1000); // Increased retries and delay
      
      if (healthResult.success) {
        if (healthResult.offline) {
          // We're in offline mode but the health check succeeded (offline mode is enabled)
          setBackendStatus('offline');
          return false;
        } else {
          // Backend is up and running
          setBackendStatus('up');
          return true;
        }
      } else if (healthResult.offlineEnabled) {
        // Health check failed but auto-switched to offline mode
        setBackendStatus('offline');
        toast.info(
          <div>
            <strong>Switched to offline mode</strong>
            <p>Could not connect to the backend server. Using cached data.</p>
            <Button 
              variant="primary" 
              size="sm"
              onClick={() => {
                toast.dismiss();
                checkBackendServer(true);
              }}
              className="mt-2"
            >
              <i className="fas fa-sync-alt me-2"></i> Retry Connection
            </Button>
          </div>,
          { autoClose: 5000 }
        );
        return false;
      } else {
        setBackendStatus('down');
        if (showToastOnError) {
          // Show a toast with retry button
          toast.error(
            <div>
              <strong>Backend server connection issue</strong>
              <p>The application can't connect to the backend server.</p>
              <p className="text-info">You can continue in offline mode with limited functionality.</p>
              <div className="mt-3 d-flex flex-column gap-2">
                <div className="d-flex gap-2">
                  <Button 
                    variant="primary" 
                    onClick={() => {
                      toast.dismiss();
                      checkBackendServer();
                    }}
                    className="mb-2 flex-grow-1"
                  >
                    <i className="fas fa-sync-alt me-2"></i> Retry Connection
                  </Button>
                  
                  <Button 
                    variant="secondary" 
                    onClick={() => {
                      setOfflineMode(true);
                      toast.dismiss();
                    }}
                    className="mb-2 flex-grow-1"
                  >
                    <i className="fas fa-cloud-download-alt me-2"></i> Use Offline Mode
                  </Button>
                </div>
                
                <div className="alert alert-info p-2 mb-2">
                  <strong>If the backend is not running:</strong>
                  <p className="mb-1 mt-1">Start it using:</p>
                  <pre className="bg-dark text-light p-2 mb-0 rounded">
                    <code>
                      {navigator.platform.includes('Win') 
                        ? 'start_backend.bat' 
                        : './start_backend.sh'}
                    </code>
                  </pre>
                </div>
              </div>
            </div>, 
            {
              autoClose: false,
              closeOnClick: false,
              draggable: false,
              closeButton: true
            }
          );
        }
        return false;
      }
    } catch (error) {
      console.error('Error checking backend health:', error);
      setBackendStatus('down');
      return false;
    }
  };

  // Initial backend check on component mount
  useEffect(() => {
    const initialCheck = async () => {
      // First attempt silently to avoid showing error immediately
      const isUp = await checkBackendServer(false);
      
      // If first check fails, wait a bit and try again with toast
      if (!isUp) {
        // Wait for any potential startup delay
        setTimeout(() => checkBackendServer(true), 3000);
      }
    };
    
    initialCheck();
    
    // Set up a listener for online/offline network status
    const handleNetworkChange = () => {
      if (navigator.onLine && backendStatus !== 'up') {
        // If we just came back online, check if backend is available
        checkBackendServer(false);
      }
    };
    
    window.addEventListener('online', handleNetworkChange);
    window.addEventListener('offline', () => setOfflineMode(true));
    
    return () => {
      window.removeEventListener('online', handleNetworkChange);
      window.removeEventListener('offline', () => setOfflineMode(true));
    };
  }, [backendStatus]); // Include backendStatus in dependencies

  return (
    <Router>
      <div className="App">
        <OfflineIndicator />
        <Navbar />
        <div className="container py-4">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/product/:id" element={<ProductDetailPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </div>
        <ToastContainer
          position="bottom-right"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      </div>
    </Router>
  );
}

export default App;