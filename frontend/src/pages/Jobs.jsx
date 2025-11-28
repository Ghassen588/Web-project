import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom'; // Import Link
import TopNavigation from '../components/TopNavigation';
import Avatar from '../components/Avatar';
import api from '../api/config';

const Jobs = () => {
    const [jobs, setJobs] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [newJob, setNewJob] = useState({ title: '', description: '', salary: '', location: '' });
    const userRole = localStorage.getItem('user_role');

    const fetchJobs = async () => {
        try {
            const res = await api.get('/jobs/');
            setJobs(res.data);
        } catch (err) { console.error(err); }
    };

    useEffect(() => { fetchJobs(); }, []);

    const handleCreateJob = async (e) => {
        e.preventDefault();
        await api.post('/jobs/create', newJob);
        setShowForm(false);
        setNewJob({ title: '', description: '', salary: '', location: '' });
        fetchJobs();
    };

    const handleApply = async (jobId) => {
        try {
            await api.post(`/jobs/${jobId}/apply`);
            alert('Applied successfully!');
        } catch (err) { alert(err.response?.data?.message || 'Error applying'); }
    };

    const handleSave = async (jobId) => {
        await api.post(`/jobs/${jobId}/save`);
        fetchJobs();
    };

    const handleRate = async (jobId, stars) => {
        await api.post(`/jobs/${jobId}/rate`, { stars });
        fetchJobs();
    };

    return (
        <>
            <TopNavigation />
            <div className="page-container">
                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px'}}>
                    <h2>Internships & Jobs</h2>
                    {userRole === 'recruiter' && (
                        <button onClick={() => setShowForm(!showForm)}>{showForm ? 'Cancel' : '+ Post Job'}</button>
                    )}
                </div>

                {showForm && (
                    <div className="card" style={{borderLeft: '4px solid #0a66c2'}}>
                        <h3>Post New Job</h3>
                        <form onSubmit={handleCreateJob}>
                            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px'}}>
                                <input placeholder="Job Title" value={newJob.title} onChange={(e) => setNewJob({...newJob, title: e.target.value})} required />
                                <input placeholder="Location" value={newJob.location} onChange={(e) => setNewJob({...newJob, location: e.target.value})} required />
                            </div>
                            <input placeholder="Salary" value={newJob.salary} onChange={(e) => setNewJob({...newJob, salary: e.target.value})} />
                            <textarea placeholder="Description" value={newJob.description} onChange={(e) => setNewJob({...newJob, description: e.target.value})} required style={{height: '100px'}} />
                            <button type="submit">Publish Job</button>
                        </form>
                    </div>
                )}

                <div className="job-list">
                    {jobs.map(job => (
                        <div key={job.id} className="card job-card" style={{display: 'flex', gap: '15px'}}>
                            {/* 1. Clickable Avatar */}
                            {/* Note: backend/routes/jobs.py needs to send 'recruiter_id' in get_jobs for this link to work perfectly. 
                                If it's missing, you can remove the Link wrapper temporarily. */}
                            <Avatar name={job.recruiter} image={job.recruiter_pic} size="50px" />
                            
                            <div style={{flex: 1}}>
                                <div style={{display: 'flex', justifyContent: 'space-between'}}>
                                    <h3 style={{margin: 0, color: '#0a66c2'}}>{job.title}</h3>
                                    {userRole === 'student' && (
                                        <button 
                                            onClick={() => handleSave(job.id)}
                                            style={{background: 'none', color: job.is_saved ? '#0a66c2' : '#666', border: '1px solid #ccc', padding: '5px 10px'}}
                                        >
                                            {job.is_saved ? '★ Saved' : '☆ Save'}
                                        </button>
                                    )}
                                </div>
                                
                                <p style={{color: '#666', fontSize: '0.9rem', margin: '5px 0'}}>
                                    <strong>{job.recruiter}</strong> • {job.location}
                                </p>
                                <p style={{margin: '10px 0', whiteSpace: 'pre-wrap'}}>{job.description}</p>
                                
                                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', borderTop: '1px solid #eee', paddingTop: '10px'}}>
                                    <span style={{background: '#eef3f8', padding: '5px 10px', borderRadius: '5px', fontSize: '0.8rem', color: '#666'}}>💰 {job.salary || 'N/A'}</span>
                                    
                                    <div style={{display: 'flex', alignItems: 'center', gap: '5px'}}>
                                        <span style={{color: '#f5c344', fontWeight: 'bold'}}>★ {job.rating}</span>
                                        {userRole === 'student' && (
                                            <select 
                                                onChange={(e) => handleRate(job.id, parseInt(e.target.value))}
                                                style={{width: 'auto', padding: '2px', fontSize: '0.8rem', margin: 0}}
                                            >
                                                <option value="">Rate</option>
                                                {[1,2,3,4,5].map(s => <option key={s} value={s}>{s}</option>)}
                                            </select>
                                        )}
                                    </div>
                                    
                                    {userRole === 'student' && <button onClick={() => handleApply(job.id)} style={{padding: '5px 15px', borderRadius: '20px'}}>Apply Now</button>}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </>
    );
};
export default Jobs;