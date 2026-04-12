import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function ViewRequests() {
  // Grab the vault ID so we know which hospital is looking at the page
  const bankId = localStorage.getItem('userId'); 
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRequests = async () => {
      if (!bankId) return; // Wait until we know who the hospital is

      try {
        // Hit our new endpoint with the bankId attached!
        const response = await axios.get(`http://127.0.0.1:8000/api/requests/pending/${bankId}`);
        if (response.data.status === 'success') {
          setRequests(response.data.data);
        }
      } catch (error) {
        console.error("Error fetching requests:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchRequests();
  }, [bankId]);

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h2>Live Blood Requests</h2>
        <p>Manage urgent patient requests (Sorted by closest to your hospital)</p>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--muted)' }}>
          Locating nearby requests...
        </div>
      ) : requests.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--muted)' }}>
          No pending blood requests at this time. All clear!
        </div>
      ) : (
        <div className="grid-2">
          {requests.map((req) => (
            <div className="card" key={req.RequestID}>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                  <div className="blood-badge selected" style={{ margin: 0, cursor: 'default' }}>
                    <div className="type" style={{ fontSize: '1.2rem' }}>{req.BloodGroup}</div>
                  </div>
                  <span className="badge badge-warning" style={{ fontSize: '13px' }}>{req.Units} Units Needed</span>
                </div>
                
                {/* 📍 NEW DISTANCE DISPLAY */}
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--teal)' }}>{req.DistanceKM} km away</div>
                    <div style={{ fontSize: '12px', color: 'var(--muted)' }}>#{req.RequestID}</div>
                </div>
              </div>

              <div style={{ marginBottom: '1.5rem', paddingLeft: '5px' }}>
                <div style={{ fontWeight: 600, fontSize: 16, color: '#1a1a18', marginBottom: 6 }}>👤 {req.PatientName}</div>
                <div style={{ fontSize: 14, color: "var(--muted)", marginBottom: 4 }}>📍 {req.City}</div>
                <div style={{ fontSize: 14, color: "var(--muted)", marginBottom: 4 }}>📞 {req.Phone}</div>
                <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 10 }}>Requested: {req.Date}</div>
              </div>

              <button className="btn-primary" style={{ width: '100%', background: 'var(--teal)' }}>
                Contact Patient
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}