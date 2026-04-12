import React from 'react';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div style={{ position: 'relative', overflow: 'hidden', minHeight: 'calc(100vh - 56px)', backgroundColor: '#fff', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>

      {/* TEXT CONTENT */}
      <div style={{ zIndex: 10, textAlign: 'center', padding: '2rem', marginTop: '-10vh' }}>
        <h1 style={{ fontSize: '3.5rem', fontWeight: '800', color: '#1a1a18', marginBottom: '1rem', letterSpacing: '-1.5px' }}>
          Every drop <span style={{ color: '#E24B4A' }}>counts.</span>
        </h1>
        <p style={{ fontSize: '1.2rem', color: '#6b6b67', marginBottom: '2.5rem', maxWidth: '600px', lineHeight: '1.6', marginInline: 'auto' }}>
          Raktkosh connects blood donors, patients, and blood banks across India. Join the network today.
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <Link to="/register" style={{ textDecoration: 'none', padding: '14px 28px', background: '#E24B4A', color: 'white', borderRadius: '50px', fontWeight: '600', fontSize: '16px', boxShadow: '0 4px 14px rgba(226, 75, 74, 0.3)' }}>
            Register as donor
          </Link>
          <Link to="/request" style={{ textDecoration: 'none', padding: '14px 28px', background: 'white', color: '#1a1a18', border: '2px solid #eaeaea', borderRadius: '50px', fontWeight: '600', fontSize: '16px' }}>
            Request blood
          </Link>
        </div>
      </div>

      {/* DYNAMIC RED WAVE */}
      <div style={{ position: 'absolute', bottom: 0, left: 0, width: '100%', lineHeight: 0 }}>
        <svg viewBox="0 0 1440 320" style={{ display: 'block', width: '100%', height: 'auto' }}>
          <path fill="#E24B4A" fillOpacity="0.8">
            <animate attributeName="d" dur="8s" repeatCount="indefinite"
              values="
                M0,160L48,170.7C96,181,192,203,288,197.3C384,192,480,160,576,149.3C672,139,768,149,864,170.7C960,192,1056,224,1152,213.3C1248,203,1344,149,1392,122.7L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z;
                M0,224L48,213.3C96,203,192,181,288,176C384,171,480,181,576,197.3C672,213,768,235,864,224C960,213,1056,171,1152,160C1248,149,1344,171,1392,181.3L1440,192L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z;
                M0,160L48,170.7C96,181,192,203,288,197.3C384,192,480,160,576,149.3C672,139,768,149,864,170.7C960,192,1056,224,1152,213.3C1248,203,1344,149,1392,122.7L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z
              "
            />
          </path>
        </svg>
      </div>
    </div>
  );
}