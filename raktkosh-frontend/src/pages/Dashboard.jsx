import React, { useState } from 'react';
import axios from 'axios';

export default function Dashboard() {
  const [city, setCity] = useState("");
  const [drives, setDrives] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault(); setLoading(true); setError(""); setDrives([]);
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/nearest-drives?city=${city}`);
      if (response.data.status === 'success') {
        setDrives(response.data.data || []);
        setSearched(true);
      }
    } catch (err) { 
      setError(err.response?.data?.detail || "Error fetching drives."); 
    } finally { 
      setLoading(false); 
    }
  };

  // Helper function to make the date look like a calendar ticket
  const parseDate = (dateStr) => {
    if (!dateStr) return { month: "---", day: "--" };
    const d = new Date(dateStr);
    return { 
      month: d.toLocaleString("default", { month: "short" }).toUpperCase(), 
      day: d.getDate() 
    };
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h2>Find donation drives</h2>
        <p>See upcoming drives near you, sorted by distance</p>
      </div>
      
      <div className="card" style={{ marginBottom: "1.25rem" }}>
        <form onSubmit={handleSearch} style={{ display: "flex", gap: "10px", alignItems: "flex-end", flexWrap: "wrap" }}>
          <div className="field" style={{ flex: 1, marginBottom: 0, minWidth: "200px" }}>
            <label>Enter your city</label>
            <input type="text" placeholder="e.g. Mumbai, Pune, Delhi" value={city} onChange={(e) => setCity(e.target.value)} required />
          </div>
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? "Searching..." : "Search drives"}
          </button>
        </form>
      </div>
      
      {error && <div className="alert alert-error">{error}</div>}
      
      {searched && !loading && drives.length === 0 && !error && (
        <div className="card" style={{ textAlign: "center", padding: "2.5rem", color: "var(--muted)" }}>
          No upcoming drives found near <strong>{city}</strong> right now.
        </div>
      )}
      
      {drives.map((drive, i) => {
        const { month, day } = parseDate(drive.date);
        return (
          <div className="drive-card" key={i}>
            <div className="drive-date-box">
              <div className="month">{month}</div>
              <div className="day">{day}</div>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 4, color: '#1a1a18' }}>{drive.name}</div>
              <div style={{ fontSize: 14, color: "var(--muted)" }}>📍 {drive.address}</div>
              <div style={{ fontSize: 13, color: "var(--muted)", marginTop: 4 }}>⏰ {drive.time}</div>
            </div>
            <div style={{ textAlign: "right" }}>
              {drive.distance_km !== null && (
                <div style={{ fontWeight: 600, fontSize: 15, color: "var(--teal)" }}>
                  {drive.distance_km} km away
                </div>
              )}
              <span className="badge badge-success" style={{ marginTop: 6, display: "inline-block" }}>Upcoming</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}