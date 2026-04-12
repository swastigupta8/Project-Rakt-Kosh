import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true); setError('');

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/users/login', {
        Email: email, Password: password
      });

      if (response.data.status === 'success') {
        localStorage.setItem('userRole', response.data.role);
        localStorage.setItem('userId', response.data.id);
        window.location.href = '/'; 
      }
    } catch (error) {
      if (error.response?.status === 401) {
        setError('Invalid email or password.');
      } else {
        setError('Failed to connect to the server.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h2>Welcome back</h2>
        <p>Log in to your Raktkosh account</p>
      </div>
      
      <div className="card" style={{ maxWidth: 400, margin: '0 auto' }}>
        <form onSubmit={handleLogin}>
          <div className="field">
            <label>Email address</label>
            <input type="email" placeholder="email@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="field">
            <label>Password</label>
            <input type="password" placeholder="Your password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          
          {error && <div className="alert alert-error">{error}</div>}
          
          <button className="btn-primary" type="submit" disabled={loading} style={{ width: "100%", marginTop: "0.5rem" }}>
            {loading ? "Logging in..." : "Log in"}
          </button>
          
          <p style={{ marginTop: "1rem", fontSize: 13, color: "var(--muted)", textAlign: "center" }}>
            Don't have an account? <Link to="/register" style={{ color: "var(--red)" }}>Register</Link>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Login;