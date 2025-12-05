import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './AddPet.css';

const AddPet = () => {
  const navigate = useNavigate();
  
  const [form, setForm] = useState({
    name: '',
    species: '',
    breed: '',
    image: null
  });
  
  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("user"));
    if (!user || user.role !== "admin") {
      navigate("/");
    }
  }, [navigate]);


  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: files ? files[0] : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name || !form.species) {
      alert('Name and species are required!');
      return;
    }
    
    const formData = new FormData();
    for (const key in form) {
      if (form[key]) formData.append(key, form[key]);
    }

    try {
      const res = await fetch('http://localhost:8000/pets/add', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.message || 'Failed to add pet');
      }
      
      const data = await res.json();
      alert(data.message || 'Pet added successfully!');
      navigate('/pets');
    } catch(err) {
      console.error('Error submitting form:', err);
      alert('Failed to add pet.See console for details.');
    }
  };

  return (
    <div className="add-pet-page">
      <h2>Add a New Pet</h2>
      <form onSubmit={handleSubmit} className="add-pet-form">
        <input type="text" name="name" placeholder="Pet Name" required onChange={handleChange} />
        <input type="text" name="species" placeholder="Species" required onChange={handleChange} />
        <input type="text" name="breed" placeholder="Breed" onChange={handleChange} />
        <input type="file" name="image" accept="image/*" onChange={handleChange} />
        <button type="submit">Add Pet</button>
      </form>
    </div>
  );
};

export default AddPet;
