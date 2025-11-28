import React, { useEffect, useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import TopNavigation from '../components/TopNavigation';
import Avatar from '../components/Avatar';
import api from '../api/config';

const SearchResults = () => {
    const [results, setResults] = useState({ users: [], jobs: [] });
    const location = useLocation();
    const query = new URLSearchParams(location.search).get('q');

    useEffect(() => {
        const fetchResults = async () => {
            if (query) {
                const res = await api.get(`/search?q=${query}&type=all`);
                setResults(res.data);
            }
        };
        fetchResults();
    }, [query]);

    return (
        <>
            <TopNavigation />
            <div className="page-container">
                <h2>Results for "{query}"</h2>
                
                <div className="section">
                    <h3>People</h3>
                    {results.users.length === 0 ? <p>No users found.</p> : (
                        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '15px'}}>
                            {results.users.map(u => (
                                <Link to={`/user/${u.id}`} key={u.id} style={{textDecoration: 'none'}}>
                                    <div className="card" style={{display: 'flex', alignItems: 'center', gap: '15px', transition: 'transform 0.2s', cursor: 'pointer'}}>
                                        <Avatar name={u.name} size="50px" />
                                        <div>
                                            <div style={{color: '#0a66c2', fontWeight: 'bold'}}>{u.name}</div>
                                            <small style={{color: '#666'}}>{u.role}</small>
                                        </div>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    )}
                </div>

                <div className="section" style={{marginTop: '30px'}}>
                    <h3>Jobs</h3>
                    {results.jobs.length === 0 ? <p>No jobs found.</p> : (
                        results.jobs.map(j => (
                            <div key={j.id} className="card job-card">
                                <h3>{j.title}</h3>
                                <p style={{margin: '5px 0'}}>{j.company} • {j.location}</p>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </>
    );
};
export default SearchResults;