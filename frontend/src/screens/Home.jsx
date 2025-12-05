import React, { useEffect } from 'react';
import './Home.css';
import logo from '../assets/logo.jpg';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();
  
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "auto";
    };
  }, []);

  return (
    <div className="home-wrapper">
      <div className="home-page">
        <header className="header">
          <h1>Welcome to PetAdopt</h1>
          <p>Your friendly pet adoption agency!</p>
        </header>

        <div className="logo-container">
          <img src={logo} alt="Pet Adoption Logo" className="logo" />
        </div>
        <section className="cta">
          <h2>Ready to adopt?</h2>
          <button className="cta-button" onClick={() => navigate('/pets')}>
            View Pets
          </button>
	  <p>Find your new best friend today!</p>
        </section>
      </div>
    </div>
  );
};

export default Home;
