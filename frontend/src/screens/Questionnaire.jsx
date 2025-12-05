import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./Questionnaire.css";

const Questionnaire = () => {
  const [formData, setFormData] = useState({
    pets: "",
    children: "",
    homeType: "",
    outdoorSpace: "",
    hoursAlone: "",
  });
  const location = useLocation();
  const pet = location.state?.pet;

  const [statusMessage, setStatusMessage] = useState("");

  const navigate = useNavigate();
	
  useEffect(() => {
    if (!pet) {
      navigate("/pets");
    }
  }, [pet, navigate]);

  if (!pet) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const user = JSON.parse(localStorage.getItem("user"));

    const submission = {
      ...formData,
      pet_id: pet.id,
      userEmail: user?.email || "",
    };

    try {
      const response = await fetch("http://localhost:8000/api/questionnaire", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(submission),
      });

      if (!response.ok) {
        throw new Error("Failed to submit questionnaire");
      }else{
        navigate('/my-applications')
      }

      const result = await response.json();
      setStatusMessage("Successfully submitted!");
      
    } catch (error) {
      console.error("Submission error:", error);
      setStatusMessage("There was an error. Please try again.");
    }
  };

  return (
    <div className="questionnaire-container">
      {pet && (
	<div className="selected-pet-info">
	  <h3>You're applying for: {pet.name}</h3>
	  <img
	    src={`http://localhost:8000/uploads/${pet.image}`}
	    alt={pet.name}
	    className="selected-pet-image"
	  />
	</div>
      )}
      <h2>Questionnaire</h2>
      <p>
        Please answer the following questions as accurately as possible in
        order to match you to your perfect pet!
      </p>
      <form onSubmit={handleSubmit}>
        <label>Do you currently own any other pets? If so, what are they?</label>
        <input
          type="text"
          name="pets"
          value={formData.pets}
          onChange={handleChange}
          required
        />

        <label>Are there any children in your household?</label>
        <input
          type="text"
          name="children"
          value={formData.children}
          onChange={handleChange}
          required
        />

        <label>What type of home do you currently reside in?</label>
        <input
          type="text"
          name="homeType"
          value={formData.homeType}
          onChange={handleChange}
          required
        />

        <label>How much outdoor space do you have? (Include fencing)</label>
        <input
          type="text"
          name="outdoorSpace"
          value={formData.outdoorSpace}
          onChange={handleChange}
          required
        />

        <label>On average, how many hours a day will this animal be left home alone?</label>
        <input
          type="text"
          name="hoursAlone"
          value={formData.hoursAlone}
          onChange={handleChange}
          required
        />
        <button>Submit</button>
      </form>

      {statusMessage && <p>{statusMessage}</p>}
    </div>
  );
};

export default Questionnaire;
