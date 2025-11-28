import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom'; // Added Link
import api from '../api/config';

const Signin = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await api.post('/auth/signin', { email, password });
            if (res.status === 200) {
                localStorage.setItem('user_role', res.data.role); 
                navigate('/jobs'); // Redirects to Jobs after login
            }
        } catch (error) {
            alert('Login failed. Check credentials.');
        }
    };

    return (
        <div className="auth-container">
            <h2>Sign In to Forstek</h2>
            <form onSubmit={handleSubmit}>
                <input type="email" placeholder="Email" onChange={(e) => setEmail(e.target.value)} required />
                <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} required />
                <button type="submit">Login</button>
            </form>
            <p style={{marginTop: '15px'}}>
                Don't have an account? <Link to="/signup">Sign Up here</Link>
            </p>
        </div>
    );
};

export default Signin;