import React, { useState } from 'react';
import { Link, useNavigate } from "react-router-dom";
import "./Register.css";

function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      alert("Passwords do not match.");
      return;
    }

    const data = { email, password, role: "user" };

    try {
      const response = await fetch("http://localhost:8000/users/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (response.ok) {
        const loginResponse = await fetch("http://localhost:8000/users/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        const loginResult = await loginResponse.json();

        if (loginResponse.ok) {
          localStorage.setItem(
            "user",
            JSON.stringify({
              email: email,
              role: loginResult.user.role,
            })
          );
          alert("Registration and login successful!");

          navigate(loginResult.role === "admin" ? "/admin" : "/pets");
          window.location.reload();
        } else {
          alert("Registration succeeded but automatic login failed.");
        }
      } else {
        alert(result.error || "Registration failed");
      }
    } catch (error) {
      console.error("Registration error:", error);
    }
  };

  return (
    <div className="container">
      <div>
        <h2 className="header">Pet Adoption <br /> Register</h2>
        <form onSubmit={handleSignup} noValidate>
          <label>Email</label>
          <input
            className="input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>Password</label>
          <input
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <label>Confirm Password</label>
          <input
            className="input"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />

          <div className="button-wrapper">
            <button type="submit" className="submit-button">Register</button>
          </div>

          <div className="login-redirect">
            <span>Already have an account? </span>
            <Link to="/Login">Login</Link>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Register;

