import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./NavBar.css";
import logo from "../assets/logo.jpg";

export default function NavBar() {
  const [user,setUser] = useState(() => {
    const storedUser = localStorage.getItem("user");
    return storedUser ? JSON.parse(storedUser) : null;
  });

  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    } else {
      setUser(null);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("user");
    setUser(null);
    navigate("/");
  };

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Link to="/" className="nav-logo">
	        <img src={logo} alt="Logo" className="logo-image" />
	        <span className="site-title">PetAdopt</span>
        </Link>
	<Link to="/pets" className="nav-link">Pets</Link>
	
	{user?.role === "user" && <Link to="/my-applications" className="nav-link">My Applications</Link>}

        {user?.role === "admin" && (
          <>
            <Link to="/add-pet" className="nav-link">Add Pet</Link>
            <Link to="/admin-register" className="nav-link">Create Admin</Link>
	    <Link to="/admin-questionnaires" className="nav-link">Questionnaires</Link>
          </>
        )}
      </div>
      <div className="navbar-right">
        {user ? (
          <div className="user-info">
            <span className="user-email">{user.email}</span>
            <button onClick={handleLogout} className="logout-button">Logout</button>
          </div>
        ) : (
          <>
            <Link to="/login" className="nav-button">Sign In</Link>
            <Link to="/register" className="nav-button">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}
