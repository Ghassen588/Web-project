import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import TopNavigation from '../components/TopNavigation';
import Avatar from '../components/Avatar';
import api from '../api/config';

const Applications = () => {
    const [apps, setApps] = useState([]);
    const role = localStorage.getItem('user_role');

    const fetchApps = async () => {
        try {
            const res = await api.get('/applications/');
            setApps(res.data);
        } catch (err) { console.error(err); }
    };

    useEffect(() => { fetchApps(); }, []);

    const handleStatusUpdate = async (appId, newStatus) => {
        try {
            await api.put(`/applications/${appId}/status`, { status: newStatus });
            fetchApps(); 
        } catch (err) { alert('Error updating status'); }
    };

    return (
        <>
            <TopNavigation />
            <div className="page-container">
                <h2>{role === 'student' ? 'My Applications' : 'Candidate Management'}</h2>
                <div className="apps-list">
                    {apps.length === 0 ? (
                        <div className="card" style={{textAlign: 'center', padding: '40px', color: '#666'}}>No applications found.</div>
                    ) : (
                        apps.map(app => (
                            <div key={app.id} className="card" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                                <div style={{display: 'flex', gap: '15px', alignItems: 'center'}}>
                                    <Avatar name={role === 'student' ? app.company : app.applicant_name} size="50px" />
                                    <div>
                                        <h3 style={{marginBottom: '4px', fontSize: '1.1rem'}}>{app.job_title}</h3>
                                        <div style={{color: '#666', fontSize: '0.9rem'}}>
                                            {role === 'recruiter' ? (
                                                <span>
                                                    Applicant: 
                                                    <Link to={`/user/${app.applicant_id}`} style={{marginLeft: '5px', color: '#0a66c2', fontWeight: 'bold', textDecoration: 'none'}}>
                                                        {app.applicant_name}
                                                    </Link>
                                                </span>
                                            ) : (
                                                <span>at <strong>{app.company}</strong></span>
                                            )}
                                            <span style={{margin: '0 8px'}}>•</span>
                                            <small>Applied: {app.date}</small>
                                        </div>
                                    </div>
                                </div>

                                <div style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '10px'}}>
                                    <span className={`status-badge ${app.status}`}>{app.status}</span>
                                    {role === 'recruiter' && app.status === 'Pending' && (
                                        <div style={{display: 'flex', gap: '8px'}}>
                                            <button onClick={() => handleStatusUpdate(app.id, 'Accepted')} style={{backgroundColor: 'var(--success)', padding: '6px 12px', fontSize: '0.8rem'}}>✔ Accept</button>
                                            <button onClick={() => handleStatusUpdate(app.id, 'Refused')} style={{backgroundColor: 'var(--danger)', padding: '6px 12px', fontSize: '0.8rem'}}>✖ Reject</button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </>
    );
};
export default Applications;