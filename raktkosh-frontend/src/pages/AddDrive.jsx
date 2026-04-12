import React, { useState } from 'react';
import axios from 'axios';

export default function AddDrive() {
  const bankId = localStorage.getItem('userId');
  const [form, setForm] = useState({ DriveName: "", DriveDate: "", StartTime: "", EndTime: "", City: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault(); setError(""); setSuccess(""); setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/drives/new', {
        BankID: parseInt(bankId),
        DriveName: form.DriveName,
        DriveDate: form.DriveDate,
        StartTime: form.StartTime + ":00", // Required for SQL format
        EndTime: form.EndTime + ":00",
        City: form.City
      });

      if (response.data.status === 'success') {
        setSuccess(`✅ ${response.data.message}`);
        setForm({ DriveName: "", DriveDate: "", StartTime: "", EndTime: "", City: "" });
      }
    } catch (err) {
      setError("❌ Failed to schedule drive. Check your connection or city name.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h2>Schedule Donation Drive</h2>
        <p>Organize a local blood camp to collect donations</p>
      </div>

      <div className="card" style={{ maxWidth: 600, margin: '0 auto' }}>
        <form onSubmit={handleSubmit}>
          
          <div className="field">
            <label>Drive Name</label>
            <input name="DriveName" placeholder="e.g. City Center Summer Drive" value={form.DriveName} onChange={handleChange} required />
          </div>
          
          <div className="field-row">
            <div className="field">
              <label>City (For Location Tracking)</label>
              <input name="City" placeholder="Pune" value={form.City} onChange={handleChange} required />
            </div>
            <div className="field">
              <label>Drive Date</label>
              <input name="DriveDate" type="date" value={form.DriveDate} onChange={handleChange} required />
            </div>
          </div>
          
          <div className="field-row">
            <div className="field">
              <label>Start Time</label>
              <input name="StartTime" type="time" value={form.StartTime} onChange={handleChange} required />
            </div>
            <div className="field">
              <label>End Time</label>
              <input name="EndTime" type="time" value={form.EndTime} onChange={handleChange} required />
            </div>
          </div>

          {error && <div className="alert alert-error" style={{ marginTop: '1rem' }}>{error}</div>}
          {success && <div className="alert alert-success" style={{ marginTop: '1rem' }}>{success}</div>}

          <div className="btn-row" style={{ marginTop: '1.5rem' }}>
            <button className="btn-primary" type="submit" disabled={loading} style={{ background: '#0056b3' }}>
              {loading ? "Scheduling & Geocoding..." : "Schedule Drive"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}