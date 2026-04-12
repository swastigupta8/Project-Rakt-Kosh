import React, { useState } from 'react';
import axios from 'axios';

const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

function SearchBlood() {
  const [bloodGroup, setBloodGroup] = useState('A+');
  const [city, setCity] = useState('');
  const [results, setResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true); setError(''); setHasSearched(true); setResults([]);

    try {
      const encodedBlood = encodeURIComponent(bloodGroup);
      const response = await axios.get(`http://127.0.0.1:8000/api/inventory/search?blood_group=${encodedBlood}&city=${city}`);
      if (response.data.status === 'success') {
        setResults(response.data.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to search. Check backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h2>Find Blood Near You</h2>
        <p>Search live hospital inventories sorted by distance.</p>
      </div>

      <div className="card" style={{ marginBottom: "1.25rem" }}>
        <form onSubmit={handleSearch}>
          <div className="field">
            <label>Select Blood Group</label>
            <div className="blood-grid">
              {BLOOD_GROUPS.map((g) => (
                <div key={g} className={`blood-badge ${bloodGroup === g ? "selected" : ""}`} onClick={() => setBloodGroup(g)} style={{ cursor: 'pointer' }}>
                  <div className="type">{g}</div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="field" style={{ marginTop: '1rem' }}>
            <label>Enter your city</label>
            <div style={{ display: "flex", gap: "10px", alignItems: "flex-end" }}>
              <input type="text" placeholder="e.g. Mumbai, Pune" value={city} onChange={(e) => setCity(e.target.value)} required style={{ flex: 1 }} />
              <button className="btn-primary" type="submit" disabled={loading}>
                {loading ? 'Scanning...' : 'Search'}
              </button>
            </div>
          </div>
        </form>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {!loading && hasSearched && results.length === 0 && !error && (
        <div className="card" style={{ textAlign: "center", padding: "2.5rem", color: "var(--muted)" }}>
          No {bloodGroup} blood currently available near <strong>{city}</strong>.
        </div>
      )}

      {results.length > 0 && (
        <div style={{ display: 'grid', gap: '15px' }}>
          {results.map((item) => (
            <div key={item.BagID} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ margin: '0 0 5px 0', fontSize: '18px' }}>🏥 {item.HospitalName}</h3>
                <p style={{ margin: '3px 0', color: 'var(--muted)', fontSize: '14px' }}>{item.Address}</p>
                <p style={{ margin: '3px 0', color: 'var(--muted)', fontSize: '14px' }}>📞 {item.Phone}</p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ display: 'block', fontSize: '24px', fontWeight: 'bold', color: 'var(--red)' }}>{bloodGroup}</span>
                <span className="badge badge-success" style={{ marginTop: '5px', display: 'inline-block' }}>
                  📍 {item.DistanceKM} km away
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SearchBlood;