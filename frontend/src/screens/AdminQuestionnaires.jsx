import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./AdminQuestionnaires.css";


const AdminQuestionnaires = () => {
  const [questionnaires, setQuestionnaires] = useState([]);
  const navigate = useNavigate();
  
  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("user"));
    if (!user || user.role !== "admin") {
      navigate("/");
    }


    fetch("http://localhost:8000/api/questionnaires")
      .then((res) => res.json())
      .then((data) => setQuestionnaires(data))
      .catch((err) => console.error("Fetch error:", err));
  }, [navigate]);

  const handleStatusChange = async (applicationId, newStatus) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/questionnaire/status/${applicationId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      if (!response.ok) throw new Error("Failed to update status");
      
      setQuestionnaires((prev) =>
        prev.map((q) =>
          q.id === applicationId ? { ...q, status: newStatus } : q
        )
      );
    } catch (error) {
      console.error("Status update failed:", error);
      alert("Error updating status. Please try again.");
    }
  };

  const pending = questionnaires.filter(app => app.status === 'Pending');
  const completed = questionnaires.filter(app => app.status !== 'Pending');

  return (
    <div className="admin-q-container">
      <h1>Submitted Questionnaires</h1>
      <h2>Active Application</h2>
      {questionnaires.length === 0 ? (
        <p>No applications submitted yet.</p>
      ) : (
        pending.map((app) => (
          <div key={app.id} className="q-card">
            <h2>{app.pet_name} (by {app.user_email})</h2>
            <p><strong>Other Pets:</strong> {app.pets_owned}</p>
            <p><strong>Children:</strong> {app.children}</p>
            <p><strong>Home Type:</strong> {app.home_type}</p>
            <p><strong>Outdoor Space:</strong> {app.outdoor_space}</p>
            <p><strong>Hours Alone:</strong> {app.hours_alone}</p>
            <p><strong>Status:</strong> {app.status}</p>

            <div className="button-group">
              <button onClick={() => handleStatusChange(app.id, 'Approved')}>Accept</button>
              <button onClick={() => handleStatusChange(app.id, 'Rejected')}>Deny</button>
            </div>

            <p><em>Submitted: {new Date(app.submitted_at).toLocaleString()}</em></p>
          </div>
        ))
      )}

      <h3>Completed Applications</h3>
      {completed.length === 0 ? (
        <p>No completed applications.</p>
      ) : (
        completed.map((app) => (
          <div key={app.id} className="q-card">
            <h2>{app.pet_name} (by {app.user_email})</h2>
            <p><strong>Other Pets:</strong> {app.pets_owned}</p>
            <p><strong>Children:</strong> {app.children}</p>
            <p><strong>Home Type:</strong> {app.home_type}</p>
            <p><strong>Outdoor Space:</strong> {app.outdoor_space}</p>
            <p><strong>Hours Alone:</strong> {app.hours_alone}</p>
            <p><strong>Status:</strong> {app.status}</p>
            <p><em>Submitted: {new Date(app.submitted_at).toLocaleString()}</em></p>
          </div>
        ))
      )}
    </div>
  );
};

export default AdminQuestionnaires;


