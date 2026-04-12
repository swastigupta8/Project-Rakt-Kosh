import React, { useState } from 'react';
import axios from 'axios';

const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

export default function RequestBlood() {
  const userId = localStorage.getItem('userId');
  const [selectedGroup, setSelectedGroup] = useState("");
  const [units, setUnits] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault(); setError(""); setSuccess("");
    
    if (!selectedGroup) { setError("Please select a blood group."); return; }
    if (!userId) { setError("You must be logged in to submit a request."); return; }
    
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/requests/new', {
        UserID: parseInt(userId),
        BloodGroup: selectedGroup,
        UnitsRequired: Number(units)
      });
      
      if (response.data.status === 'success') {
        setSuccess(`✅ ${response.data.message}`);
        setUnits(1);
        setSelectedGroup("");
      }
    } catch (err) { 
      setError(err.response?.data?.detail || "Failed to submit request."); 
    } finally { 
      setLoading(false); 
    }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h2>Request blood</h2>
        <p>Submit a request — you'll be notified when a match is found</p>
      </div>
      
      <div className="grid-2" style={{ alignItems: "start" }}>
        <div className="card">
          <div className="card-title">New blood request</div>
          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Select blood group needed</label>
              <div className="blood-grid">
                {BLOOD_GROUPS.map((g) => (
                  <div key={g} className={`blood-badge ${selectedGroup === g ? "selected" : ""}`} onClick={() => setSelectedGroup(g)} style={{ cursor: 'pointer' }}>
                    <div className="type">{g}</div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="field" style={{ marginTop: "1rem" }}>
              <label>Units required</label>
              <input type="number" min="1" max="10" value={units} onChange={(e) => setUnits(e.target.value)} required />
            </div>
            
            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            
            <div className="btn-row">
              <button className="btn-primary" type="submit" disabled={loading || !userId}>
                {loading ? "Submitting..." : "Submit request"}
              </button>
            </div>
          </form>
        </div>
        
        <div className="card">
          <div className="card-title">How this works</div>
          <ol style={{ paddingLeft: "1.2rem", fontSize: 14, color: "var(--muted)", lineHeight: 2 }}>
            <li>Select the blood group you need</li>
            <li>Enter how many units you require</li>
            <li>Submit your request</li>
            <li>Admin portals instantly receive your live request</li>
            <li>You get contacted when a match is found in your city</li>
          </ol>
        </div>
      </div>
    </div>
  );
}