import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './MyApplications.css';

const MyApplications = () => {
  const [applications, setApplications] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) {
      navigate('/login');
      return;
    }

    const userEmail = user.email;

    fetch(`http://localhost:8000/api/my-applications?email=${userEmail}`)
      .then((res) => {
        if (!res.ok) {
          if (res.status === 404) {
	    console.warn("No applications found.");
	    return[]
     	  }
          throw new Error(`HTTP error! status ${res.status}`);
        }
	return res.json();
      })
      .then((data) => {
        if (Array.isArray(data)) {
          setApplications(data);
        } else {
          console.error('Unexpected response:', data);
          setApplications([]);
        }
      })
      .catch((err) => {
        console.error('Error fetching applications:', err);
        setApplications([]);
      });

  }, []);

  const activeApplications = applications.filter(app => app.status === 'Pending');
  const completedApplications = applications.filter(app => app.status !== 'Pending');

  return (
    <div className="my-applications-container">
      <h1>Your Submitted Applications</h1>

      {/* Active applications */}
      <h2>Active Applications</h2>
      {activeApplications.length === 0 ? (
        <p>No active applications.</p>
      ) : (
        activeApplications.map((app) => (
          <div key={app.id} className="application-card">
            <h2>{app.pet_name}</h2>
            <p><strong>Other Pets:</strong> {app.pets_owned}</p>
            <p><strong>Children:</strong> {app.children}</p>
            <p><strong>Home Type:</strong> {app.home_type}</p>
            <p><strong>Outdoor Space:</strong> {app.outdoor_space}</p>
            <p><strong>Hours Alone:</strong> {app.hours_alone}</p>
            <p><strong>Status:</strong> {app.status}</p>
            <p><em>Submitted on: {new Date(app.submitted_at).toLocaleString()}</em></p>
          </div>
        ))
      )}

      {/* Completed applications */}
      <h2>Completed Applications</h2>
      {completedApplications.length === 0 ? (
        <p>No completed applications.</p>
      ) : (
        completedApplications.map((app) => (
          <div key={app.id} className="application-card">
            <h2>{app.pet_name}</h2>
            <p><strong>Other Pets:</strong> {app.pets_owned}</p>
            <p><strong>Children:</strong> {app.children}</p>
            <p><strong>Home Type:</strong> {app.home_type}</p>
            <p><strong>Outdoor Space:</strong> {app.outdoor_space}</p>
            <p><strong>Hours Alone:</strong> {app.hours_alone}</p>
            <p><strong>Status:</strong> {app.status}</p>
            <p><em>Submitted on: {new Date(app.submitted_at).toLocaleString()}</em></p>
          </div>
        ))
      )}
    </div>
  );
};

export default MyApplications;

