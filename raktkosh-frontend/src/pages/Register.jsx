import React, { useState } from 'react';
import axios from 'axios';

function Register() {
  const [accountType, setAccountType] = useState('user'); // 'user' or 'bank'
  const [formData, setFormData] = useState({});
  const [message, setMessage] = useState('');

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage('Processing...');

    try {
      const endpoint = accountType === 'user' 
        ? 'http://127.0.0.1:8000/api/users/register' 
        : 'http://127.0.0.1:8000/api/banks/register';

      const response = await axios.post(endpoint, formData);

      if (response.data.status === 'success') {
        setMessage(`✅ ${response.data.message}`);
        setFormData({}); // Clear form
      }
    } catch (error) {
      setMessage(`❌ ${error.response?.data?.detail || "Registration failed"}`);
    }
  };

  return (
    <div style={{ maxWidth: '500px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', backgroundColor: 'white' }}>
      <h2 style={{ textAlign: 'center', color: '#d32f2f' }}>Create an Account</h2>
      
      {/* The Toggle Switch */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginBottom: '20px' }}>
        <button onClick={() => setAccountType('user')} style={{ padding: '10px', backgroundColor: accountType === 'user' ? '#d32f2f' : '#ddd', color: accountType === 'user' ? 'white' : 'black', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>Patient / Donor</button>
        <button onClick={() => setAccountType('bank')} style={{ padding: '10px', backgroundColor: accountType === 'bank' ? '#0056b3' : '#ddd', color: accountType === 'bank' ? 'white' : 'black', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>Hospital / Blood Bank</button>
      </div>

      <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        
        {/* If User is selected */}
        {accountType === 'user' && (
          <>
            <input type="text" name="FullName" placeholder="Full Name" onChange={handleInputChange} required style={{ padding: '10px' }} />
            <input type="email" name="Email" placeholder="Email" onChange={handleInputChange} required style={{ padding: '10px' }} />
            <input type="password" name="Password" placeholder="Password" onChange={handleInputChange} required style={{ padding: '10px' }} />
            <input type="text" name="PhoneNumber" placeholder="Phone Number" onChange={handleInputChange} required style={{ padding: '10px' }} />
            <select name="BloodGroup" onChange={handleInputChange} required style={{ padding: '10px' }}>
              <option value="">Select Blood Group</option>
              <option value="A+">A+</option><option value="A-">A-</option>
              <option value="B+">B+</option><option value="B-">B-</option>
              <option value="O+">O+</option><option value="O-">O-</option>
              <option value="AB+">AB+</option><option value="AB-">AB-</option>
            </select>
            <input type="text" name="City" placeholder="City (e.g. Pune, Mumbai)" onChange={handleInputChange} required style={{ padding: '10px' }} />
          </>
        )}

        {/* If Bank is selected */}
        {accountType === 'bank' && (
          <>
            <input type="text" name="Name" placeholder="Hospital Name" onChange={handleInputChange} required style={{ padding: '10px' }} />
            <input type="text" name="GovtRegistrationNo" placeholder="Govt License Number" onChange={handleInputChange} required style={{ padding: '10px' }} />
            <input type="email" name="ContactEmail" placeholder="Official Email" onChange={handleInputChange} required style={{ padding: '10px' }} />
            <input type="password" name="Password" placeholder="Password" onChange={handleInputChange} required style={{ padding: '10px' }} />
            <input type="text" name="ContactPhone" placeholder="Helpline Number" onChange={handleInputChange} required style={{ padding: '10px' }} />
            <input type="text" name="City" placeholder="City" onChange={handleInputChange} required style={{ padding: '10px' }} />
            <input type="text" name="Address" placeholder="Full Street Address" onChange={handleInputChange} required style={{ padding: '10px' }} />
          </>
        )}

        <button type="submit" style={{ padding: '10px', backgroundColor: '#28a745', color: 'white', border: 'none', cursor: 'pointer', fontWeight: 'bold' }}>Sign Up</button>
      </form>
      
      {message && <p style={{ marginTop: '20px', textAlign: 'center', fontWeight: 'bold', color: message.includes('✅') ? 'green' : 'red' }}>{message}</p>}
    </div>
  );
}

export default Register;