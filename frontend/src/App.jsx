import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import NavBar from './components/NavBar';
import Home from './screens/Home';
import ShipPackage from './screens/ShipPackage';
import BillingPage from './screens/BillingPage';
import AdminDashboard from './screens/AdminDashboard';
import AdminUserManagement from './screens/AdminUserManagement';
import PackageTracking from './screens/PackageTracking';
import ManageCustomers from './screens/ManageCustomers';
import Register from './screens/Register';
import Login from './screens/Login';

// Protected Route Component
const ProtectedRoute = ({ children, requireStaff = false }) => {
  const token = localStorage.getItem('authToken');
  const userRole = localStorage.getItem('userRole');
  
  // If not logged in, redirect to login
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  // If staff access required but user is not staff/admin
  if (requireStaff && userRole !== 'staff' && userRole !== 'admin') {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

// Admin Only Route Component
const AdminRoute = ({ children }) => {
  const token = localStorage.getItem('authToken');
  const userRole = localStorage.getItem('userRole');
  
  // If not logged in, redirect to login
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  // If not admin, redirect to home
  if (userRole !== 'admin') {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

export default function App() {
  return (
    <Router>
      <NavBar />
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        
        {/* Protected Customer Routes */}
        <Route 
          path="/track" 
          element={
            <ProtectedRoute>
              <PackageTracking />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/ship" 
          element={
            <ProtectedRoute>
              <ShipPackage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/billing" 
          element={
            <ProtectedRoute>
              <BillingPage />
            </ProtectedRoute>
          } 
        />
        
        {/* Protected Staff/Admin Routes */}
        <Route 
          path="/admin" 
          element={
            <ProtectedRoute requireStaff={true}>
              <AdminDashboard />
            </ProtectedRoute>
          } 
        />
        
        {/* Admin Only Routes */}
        <Route 
          path="/admin/users" 
          element={
            <AdminRoute>
              <AdminUserManagement />
            </AdminRoute>
          } 
        />
        <Route 
          path="/admin/customers" 
          element={
            <AdminRoute>
              <ManageCustomers />
            </AdminRoute>
          } 
        />
      </Routes>
    </Router>
  );
}
