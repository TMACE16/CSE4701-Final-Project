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
import AdminRegister from './screens/AdminRegister';


export default function App() {
  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
	<Route path="/admin-register" element={<AdminRegister />} />
	<Route path="/admin" element={<AdminDashboard />} />
		<Route path="/track" element={<PackageTracking />} />
        <Route path="/ship" element={<ShipPackage />} />
        <Route path="/billing" element={<BillingPage />} />
      </Routes>
    </>
  );
}
