import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/config';

const TopNavigation = () => {
    const navigate = useNavigate();
    const [query, setQuery] = useState('');

    const handleLogout = async () => {
        await api.post('/auth/logout');
        localStorage.removeItem('user_role');
        navigate('/signin');
    };

    const handleSearch = (e) => {
        e.preventDefault();
        if(query.trim()) {
            navigate(`/search?q=${query}`);
        }
    };

    return (
        <nav className="navbar">
            <div className="logo">Forstek</div>
            
            <form onSubmit={handleSearch} className="search-bar">
                <input 
                    type="text" 
                    placeholder="Search..." 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
            </form>

            <div className="links">
                <Link to="/forum">Forum</Link>
                <Link to="/jobs">Jobs</Link>
                <Link to="/applications">Applications</Link>
                <Link to="/notifications">🔔</Link>
                <Link to="/messages" title="Messaging">Messages</Link>
                <Link to="/myprofile">Profile</Link>
                <button onClick={handleLogout}>Logout</button>
            </div>
        </nav>
    );
};

export default TopNavigation;