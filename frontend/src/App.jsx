import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import LeadForm from './pages/LeadForm';

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isAttorney, loading } = useAuth();
  
  // Show loading indicator while checking authentication
  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }
  
  // Redirect to login if not authenticated or not an attorney
  if (!isAuthenticated() || !isAttorney()) {
    return <Navigate to="/login" />;
  }
  
  // Render children if authenticated and authorized
  return children;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public route - Lead Form */}
          <Route path="/" element={<LeadForm />} />
          
          {/* Public route - Login */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected route - Dashboard */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Fallback route - Redirect to Lead Form */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;