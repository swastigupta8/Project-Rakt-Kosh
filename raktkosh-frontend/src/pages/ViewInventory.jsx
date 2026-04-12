import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

export default function ViewInventory() {
  const bankId = localStorage.getItem('userId');
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // 🔥 NEW: State to track which blood group we are filtering by
  const [filterGroup, setFilterGroup] = useState('All');

  useEffect(() => {
    const fetchInventory = async () => {
      if (!bankId) return;
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/inventory/${bankId}`);
        if (response.data.status === 'success') {
          setInventory(response.data.data);
        }
      } catch (error) {
        console.error("Error fetching inventory:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchInventory();
  }, [bankId]);

  // 🔥 NEW: Apply the filter math before we render the table!
  const filteredInventory = filterGroup === 'All' 
    ? inventory 
    : inventory.filter(bag => bag.BloodGroup === filterGroup);

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h2>Live Blood Inventory</h2>
        <p>Manage and track your hospital's available blood units</p>
      </div>

      <div className="card">
        {/* --- THE NEW INTERACTIVE FILTER BAR --- */}
        <div style={{ marginBottom: '2rem' }}>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, marginBottom: '0.5rem', color: 'var(--text)' }}>
            Filter by Blood Group
          </label>
          <div className="blood-grid">
            {/* The "All" Button to reset the filter */}
            <div 
              className={`blood-badge ${filterGroup === 'All' ? 'selected' : ''}`} 
              onClick={() => setFilterGroup('All')} 
              style={{ cursor: 'pointer', minWidth: '80px' }}
            >
              <div className="type" style={{ fontSize: '1rem' }}>All Stock</div>
            </div>
            
            {/* The individual Blood Group Buttons */}
            {BLOOD_GROUPS.map((g) => (
              <div 
                key={g} 
                className={`blood-badge ${filterGroup === g ? 'selected' : ''}`} 
                onClick={() => setFilterGroup(g)} 
                style={{ cursor: 'pointer' }}
              >
                <div className="type">{g}</div>
                {/* Optional: Show exactly how many bags of this type exist! */}
                <div className="units">
                  {inventory.filter(b => b.BloodGroup === g).length} units
                </div>
              </div>
            ))}
          </div>
        </div>

        <hr className="divider" style={{ marginTop: 0 }} />

        {/* --- THE TABLE --- */}
        {loading ? (
          <p style={{ textAlign: 'center', padding: '2rem', color: 'var(--muted)' }}>Scanning refrigerators...</p>
        ) : filteredInventory.length === 0 ? (
          <p style={{ textAlign: 'center', padding: '2rem', color: 'var(--muted)' }}>
            {filterGroup === 'All' 
              ? "No blood bags in inventory yet!" 
              : `No ${filterGroup} bags currently in stock.`}
          </p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Bag ID</th>
                <th>Blood Group</th>
                <th>Collection Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredInventory.map((bag) => (
                <tr key={bag.BloodBagID}>
                  <td style={{ fontWeight: 500, color: 'var(--muted)' }}>#{bag.BloodBagID}</td>
                  <td><strong style={{ color: 'var(--red)', fontSize: '16px' }}>{bag.BloodGroup}</strong></td>
                  <td>{bag.CollectionDate}</td>
                  <td>
                    <span className={`badge ${bag.Status === 'Available' ? 'badge-success' : bag.Status === 'Expired' ? 'badge-danger' : 'badge-warning'}`}>
                      {bag.Status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}