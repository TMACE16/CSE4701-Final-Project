import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Login.css"; 

function Login () {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    const data = { email, password };

    try {
      // obviously the backend server needs to be running for
      // this code to work, DUH
      const response = await fetch("http://localhost:8000/users/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      const result = await response.json();

      if (response.ok) {
        localStorage.setItem(
          "user",
          JSON.stringify({
            email: result.user.email,
            role: result.user.role,
          })
        );

        navigate("/pets");
      
        window.location.reload();

      } else {
        alert(result.error || "Invalid credentials.");
      }
    } catch (error) {
      console.error("Login error:", error);
    }
  };
  return (
    <div className="container">
      <div>
        <h2 className="header">Pet Adoption <br/> Login</h2>
        <form onSubmit={handleLogin} noValidate>
          <label
            style={{
              fontSize: "18px",
              color: "#000000",
              display: "block",
              textAlign: "left",
            }}
          >
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{
              padding: "10px 15px",
              fontSize: "16px",
              border: "none",
              backgroundColor: "#D9D9D9",
              width: "100%",
              marginTop: "5px",
              marginBottom: "10px",
            }}
            required
          />

          <label
            style={{
              fontSize: "18px",
              color: "#000000",
              display: "block",
              textAlign: "left",
            }}
          >
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{
              padding: "10px 15px",
              fontSize: "16px",
              border: "none",
              backgroundColor: "#D9D9D9",
              width: "100%",
              marginTop: "5px",
              marginBottom: "10px",
            }}
            required
          />

          <button
            type="submit"
            style={{
              marginTop: "40px",
              padding: "10px 20px",
              fontSize: "18px",
              fontWeight: "bold",
              backgroundColor: "#97B4FF",
              borderRadius: "0px",
            }}
          >
            LOGIN
          </button>
        </form>
        <div style={{ textAlign: "center", marginTop: "10px" }}>
          <span style={{ fontSize: "18px", color: "#000000" }}>
            Don't have an account?{" "}
          </span>
          <Link to="/Register" style={{ fontSize: "18px", color: "#097A8B" }}>
            Register
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
