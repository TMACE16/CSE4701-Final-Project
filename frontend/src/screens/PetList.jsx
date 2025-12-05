import React, { useEffect, useState } from 'react';
import './PetList.css';
import { useNavigate } from 'react-router-dom';

const PetList = () => {
  const [temppets, settempPets] = useState([]);
  const [adoptedPets, setAdoptedPets] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Updated fetch with cache control header
    fetch('http://localhost:8000/pets/', {
      headers: {
        'Cache-Control': 'no-cache'
      }
    })
      .then(res => res.json())
      .then(data => {
        console.log(data); // Optional logging to check the structure of the data
        settempPets(data.pets);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching pets:', err);
        setLoading(false);
      });
  
    fetch("http://localhost:8000/api/questionnaires")
      .then((res) => res.json())
      .then((applications) => {
        const adoptedPetNames = applications
          .filter((app) => app.status === "Approved")
	  .map((app) => app.pet_name);

        setAdoptedPets(adoptedPetNames);
      })
      .catch((error) => console.error("Error fetching applications:", error));
  }, []);

  const pets = temppets.filter((pet) => !adoptedPets.includes(pet.name));

  // Grouping pets by species
  const groupedPets = pets.reduce((groups, pet) => {
    const { species } = pet;
    if (!groups[species]) groups[species] = [];
    groups[species].push(pet);
    return groups;
  }, {});

  const isEmpty = Object.keys(groupedPets).length === 0;

  return (
    <div className="pet-list-page">
      <h1 className="title">Available Pets</h1>

      {loading ? (
        <div className="loading">Loading pets...</div>
      ) : pets.length === 0 ? (
        <div className="no-pets">No pets available at the moment.</div>
      ) : (
        Object.keys(groupedPets).map(species => (
          <div key={species} className="species-section">
            <h2 className="species-title">{species}s</h2>
            <div className="pet-grid">
              {groupedPets[species].map(pet => (
                <div className="pet-card" key={pet.id}>
                  {pet.image && (
                    <img
                      src={`http://localhost:8000/uploads/${pet.image}`}
                      alt={pet.name}
                      className="pet-image"
                    />
                  )}
                  <h3>{pet.name}</h3>
                  <p><strong>Breed:</strong> {pet.breed || 'Unknown'}</p>
                  <button onClick={() => {
                    const user = localStorage.getItem("user");
                    if (user) {
                      navigate('/questionnaire', { state: { pet } });
                    } else {
                      navigate('/Login');
                    }
                  }}
                    className="apply-button">
                    Apply
                  </button>
                </div>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default PetList;

