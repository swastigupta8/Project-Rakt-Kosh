import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import Login from './pages/Login'; 
import Register from './pages/Register'; 
import Dashboard from './pages/Dashboard'; 
import RequestBlood from './pages/RequestBlood'; 
import AddDrive from './pages/AddDrive';
import ViewRequests from './pages/ViewRequests'; 
import ManageInventory from './pages/ManageInventory'; 
import ViewInventory from './pages/ViewInventory';     
import SearchBlood from './pages/SearchBlood';
import Home from './pages/Home';

function Navigation() {
  const location = useLocation();
  const currentRole = localStorage.getItem('userRole');

  const handleLogout = () => {
    localStorage.removeItem('userRole');
    localStorage.removeItem('userId');
    window.location.href = '/login';
  };

  return (
    <nav style={styles.nav}>
      {/* LEFT SIDE: Logo */}
      <Link to="/" style={styles.logo}>
        <div style={styles.logoDot}>+</div> Raktkosh
      </Link>

      {/* MIDDLE: Navigation Links */}
      <div style={styles.links}>
        <Link to="/" style={{ ...styles.link, ...(location.pathname === "/" ? styles.linkActive : {}) }}>Home</Link>
        
        {/* PATIENT LINKS */}
        {currentRole === 'user' && (
          <>
            <Link to="/search-blood" style={{ ...styles.link, ...(location.pathname === "/search-blood" ? styles.linkActive : {}) }}>Find Blood</Link>
            <Link to="/dashboard" style={{ ...styles.link, ...(location.pathname === "/dashboard" ? styles.linkActive : {}) }}>Find Drives</Link>
            <Link to="/request" style={{ ...styles.link, ...(location.pathname === "/request" ? styles.linkActive : {}) }}>Request Blood</Link>
          </>
        )}

        {/* ADMIN LINKS */}
        {currentRole === 'bank' && (
          <>
            <Link to="/admin/requests" style={{ ...styles.link, ...(location.pathname === "/admin/requests" ? styles.linkActive : {}) }}>Pending Requests</Link>
            <Link to="/admin/view-inventory" style={{ ...styles.link, ...(location.pathname === "/admin/view-inventory" ? styles.linkActive : {}) }}>Live Inventory</Link>
            <Link to="/admin/add-inventory" style={{ ...styles.link, ...(location.pathname === "/admin/add-inventory" ? styles.linkActive : {}) }}>Add Blood</Link>
            <Link to="/add-drive" style={{ ...styles.link, ...(location.pathname === "/add-drive" ? styles.linkActive : {}) }}>Schedule Drive</Link>
          </>
        )}
      </div>

      {/* RIGHT SIDE: Login/Logout */}
      <div style={styles.right}>
        {currentRole ? (
          <button onClick={handleLogout} style={styles.btnSecondary}>Log out</button>
        ) : (
          <>
            <Link to="/login" style={styles.btnSecondary}>Log in</Link>
            <Link to="/register" style={styles.btnPrimary}>Sign Up</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Navigation />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} /> 
        <Route path="/dashboard" element={<Dashboard />} /> 
        <Route path="/request" element={<RequestBlood />} /> 
        <Route path="/add-drive" element={<AddDrive />} /> 
        <Route path="/admin/requests" element={<ViewRequests />} /> 
        <Route path="/admin/add-inventory" element={<ManageInventory />} /> 
        <Route path="/admin/view-inventory" element={<ViewInventory />} /> 
        <Route path="/search-blood" element={<SearchBlood />} />
      </Routes>
    </BrowserRouter>
  );
}

// Teammate's Navbar Styles
const styles = {
  nav: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 1.5rem", height: "56px", background: "#ffffff", borderBottom: "1px solid rgba(0,0,0,0.08)", position: "sticky", top: 0, zIndex: 100 },
  logo: { display: "flex", alignItems: "center", gap: "8px", fontWeight: "600", fontSize: "16px", color: "#1a1a18", textDecoration: "none" },
  logoDot: { width: "26px", height: "26px", borderRadius: "50%", background: "#E24B4A", color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "16px", fontWeight: "600" },
  links: { display: "flex", gap: "4px" },
  link: { padding: "6px 12px", borderRadius: "8px", fontSize: "14px", color: "#6b6b67", textDecoration: "none" },
  linkActive: { background: "#f8f7f4", color: "#1a1a18", fontWeight: "500" },
  right: { display: "flex", alignItems: "center", gap: "8px" },
  btnPrimary: { background: "#E24B4A", color: "white", border: "none", borderRadius: "8px", padding: "7px 14px", fontSize: "13px", fontWeight: "500", cursor: "pointer", textDecoration: "none" },
  btnSecondary: { background: "transparent", color: "#1a1a18", border: "1px solid rgba(0,0,0,0.1)", borderRadius: "8px", padding: "7px 14px", fontSize: "13px", cursor: "pointer", textDecoration: "none" },
};