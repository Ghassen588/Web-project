import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom'; // Added Link
import api from '../api/config';

const Signup = () => {
    const [formData, setFormData] = useState({
        firstname: '', lastname: '', email: '', password: '', role: 'student'
    });
    const navigate = useNavigate();

    const handleChange = (e) => setFormData({...formData, [e.target.name]: e.target.value});

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post('/auth/signup', formData);
            alert('Account created! Please log in.');
            navigate('/signin');
        } catch (error) {
            alert('Signup failed. Email might be taken.');
        }
    };

    return (
        <div className="auth-container">
            <h2>Join Forstek</h2>
            <form onSubmit={handleSubmit}>
                <input name="firstname" placeholder="First Name" onChange={handleChange} required />
                <input name="lastname" placeholder="Last Name" onChange={handleChange} required />
                <input name="email" placeholder="Email" onChange={handleChange} required />
                <input type="password" name="password" placeholder="Password" onChange={handleChange} required />
                
                <div className="role-select" style={{margin: '15px 0'}}>
                    <label style={{marginRight: '15px'}}><input type="radio" name="role" value="student" defaultChecked onChange={handleChange}/> Student</label>
                    <label><input type="radio" name="role" value="recruiter" onChange={handleChange}/> Recruiter</label>
                </div>
                
                <button type="submit">Sign Up</button>
            </form>
            <p style={{marginTop: '15px'}}>
                Already have an account? <Link to="/signin">Sign In here</Link>
            </p>
        </div>
    );
};

export default Signup;