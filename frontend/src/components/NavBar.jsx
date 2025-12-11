import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./NavBar.css";
import logo from "../assets/logo.jpg";

export default function NavBar() {
  const [user, setUser] = useState(() => {
    const authToken = localStorage.getItem("authToken");
    const userRole = localStorage.getItem("userRole");
    const userEmail = localStorage.getItem("userEmail");
    
    if (authToken && userRole && userEmail) {
      return { email: userEmail, role: userRole };
    }
    return null;
  });

  const navigate = useNavigate();

  useEffect(() => {
    const authToken = localStorage.getItem("authToken");
    const userRole = localStorage.getItem("userRole");
    const userEmail = localStorage.getItem("userEmail");
    
    if (authToken && userRole && userEmail) {
      setUser({ email: userEmail, role: userRole });
    } else {
      setUser(null);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("userRole");
    localStorage.removeItem("userEmail");
    setUser(null);
    navigate("/");
  };

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Link to="/" className="nav-logo">
          <img src={logo} alt="Logo" className="logo-image" />
          <span className="site-title">QuickShip</span>
        </Link>

        {/* Show links based on login status and role */}
        {!user && (
          <>
            {/* Public links when NOT logged in */}
            <Link to="/track" className="nav-link">Track Package</Link>
          </>
        )}

        {/* Customer Links */}
        {user?.role === "customer" && (
          <>
            <Link to="/track" className="nav-link">Track Package</Link>
            <Link to="/ship" className="nav-link">Ship Package</Link>
            <Link to="/billing" className="nav-link">Billing</Link>
          </>
        )}

        {/* Staff Links */}
        {user?.role === "staff" && (
          <>
            <Link to="/admin" className="nav-link">Dashboard</Link>
            <Link to="/track" className="nav-link">Track Package</Link>
          </>
        )}

        {/* Admin Links */}
        {user?.role === "admin" && (
          <>
            <Link to="/admin" className="nav-link">Dashboard</Link>
            <Link to="/admin/users" className="nav-link">Manage Users</Link>
            <Link to="/track" className="nav-link">Track Package</Link>
          </>
        )}
      </div>

      <div className="navbar-right">
        {user ? (
          // Logged in - Show user info and logout
          <div className="user-info">
            <span className="user-email">{user.email}</span>
            <span className="user-role">({user.role})</span>
            <button onClick={handleLogout} className="logout-button">Logout</button>
          </div>
        ) : (
          // NOT logged in - Show Sign In and Register
          <>
            <Link to="/login" className="nav-button">Sign In</Link>
            <Link to="/register" className="nav-button">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}
