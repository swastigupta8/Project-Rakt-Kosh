import React, { useState } from 'react';
import axios from 'axios';

const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

export default function ManageInventory() {
  const bankId = localStorage.getItem('userId');
  const [bloodGroup, setBloodGroup] = useState("");
  const [collectionDate, setCollectionDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault(); setError(""); setSuccess("");
    
    if (!bloodGroup) { setError("Please select a blood group."); return; }
    
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/inventory/add', {
        BankID: parseInt(bankId),
        BloodGroup: bloodGroup,
        CollectionDate: collectionDate
      });
      
      if (response.data.status === 'success') {
        setSuccess(`✅ ${response.data.message}`);
        setBloodGroup("");
        setCollectionDate("");
      }
    } catch (err) { 
      setError("❌ Failed to add inventory. Check your backend connection."); 
    } finally { 
      setLoading(false); 
    }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h2>Log Blood Units</h2>
        <p>Add newly collected blood bags to your live inventory</p>
      </div>

      <div className="card" style={{ maxWidth: 500, margin: '0 auto' }}>
        <div className="card-title">Add blood unit</div>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label>Blood group — click to select</label>
            <div className="blood-grid">
              {BLOOD_GROUPS.map((g) => (
                <div key={g} className={`blood-badge ${bloodGroup === g ? "selected" : ""}`} onClick={() => setBloodGroup(g)} style={{ cursor: 'pointer' }}>
                  <div className="type">{g}</div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="field" style={{ marginTop: "1rem" }}>
            <label>Collection date</label>
            <input type="date" value={collectionDate} onChange={(e) => setCollectionDate(e.target.value)} required />
          </div>
          
          {error && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}
          
          <div className="btn-row">
            <button className="btn-primary" type="submit" disabled={loading} style={{ background: '#17a2b8' }}>
              {loading ? "Adding..." : "+ Add to inventory"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}