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

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import Home from './screens/Home';
import PackageTracking from './screens/PackageTracking';
import ShipPackage from './screens/ShipPackage';
import BillingPage from './screens/BillingPage';
import AdminDashboard from './screens/AdminDashboard';
import Register from './screens/Register';
import Login from './screens/Login';
import AdminUserManagement from './screens/AdminUserManagement';
import ManageCustomers from './screens/ManageCustomers';



export default function App() {
  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
	<Route path="/admin" element={<AdminDashboard />} />
  <Route path="/admin/users" element={<AdminUserManagement />} />
  <Route path="/admin/customers" element={<AdminUserManagement />} />
		<Route path="/track" element={<PackageTracking />} />
        <Route path="/ship" element={<ShipPackage />} />
        <Route path="/billing" element={<BillingPage />} />
      </Routes>
    </>
  );
}
