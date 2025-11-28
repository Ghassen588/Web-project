import React, { useEffect, useState } from 'react';
import TopNavigation from '../components/TopNavigation';
import api from '../api/config';
import { useNavigate } from 'react-router-dom';

const Settings = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        firstname: '', lastname: '', bio: '', 
        study_place: '', work_place: '', 
        linkedin_link: '', github_link: '',
        password: '' // Optional password field
    });

    useEffect(() => {
        const loadData = async () => {
            try {
                const res = await api.get('/profile/me');
                // Backend returns null for empty fields, convert to empty string for React inputs
                const data = res.data;
                Object.keys(data).forEach(k => { if(data[k] === null) data[k] = '' });
                setFormData(data);
            } catch(err) { console.error(err); }
        };
        loadData();
    }, []);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.put('/profile/update', formData);
            alert("Profile updated successfully!");
            navigate('/myprofile');
        } catch (err) {
            alert("Error updating profile.");
        }
    };

    return (
        <>
            <TopNavigation />
            <div className="page-container" style={{maxWidth: '800px'}}>
                <div className="card">
                    <h2 style={{borderBottom: '1px solid #eee', paddingBottom: '15px', marginBottom: '20px'}}>
                        Account Settings
                    </h2>
                    
                    <form onSubmit={handleSubmit}>
                        {/* Basic Info Section */}
                        <h4 style={{color: '#0a66c2', marginBottom: '10px'}}>Basic Information</h4>
                        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px'}}>
                            <div>
                                <label style={{fontSize: '0.9rem', fontWeight: 'bold'}}>First Name</label>
                                <input name="firstname" value={formData.firstname} onChange={handleChange} required />
                            </div>
                            <div>
                                <label style={{fontSize: '0.9rem', fontWeight: 'bold'}}>Last Name</label>
                                <input name="lastname" value={formData.lastname} onChange={handleChange} required />
                            </div>
                        </div>

                        <div style={{marginTop: '10px'}}>
                            <label style={{fontSize: '0.9rem', fontWeight: 'bold'}}>Bio / Headline</label>
                            <textarea 
                                name="bio" 
                                value={formData.bio} 
                                onChange={handleChange} 
                                rows="3"
                                placeholder="Software Engineer Student at..."
                            />
                        </div>

                        {/* Professional Info Section */}
                        <h4 style={{color: '#0a66c2', marginTop: '20px', marginBottom: '10px'}}>Professional Details</h4>
                        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px'}}>
                            <div>
                                <label style={{fontSize: '0.9rem', fontWeight: 'bold'}}>Study Place</label>
                                <input name="study_place" value={formData.study_place} onChange={handleChange} />
                            </div>
                            <div>
                                <label style={{fontSize: '0.9rem', fontWeight: 'bold'}}>Work Place</label>
                                <input name="work_place" value={formData.work_place} onChange={handleChange} />
                            </div>
                        </div>

                        {/* Links Section */}
                        <div style={{marginTop: '10px'}}>
                            <label style={{fontSize: '0.9rem', fontWeight: 'bold'}}>LinkedIn URL</label>
                            <input name="linkedin_link" value={formData.linkedin_link} onChange={handleChange} placeholder="https://linkedin.com/in/..." />
                        </div>
                        <div style={{marginTop: '10px'}}>
                            <label style={{fontSize: '0.9rem', fontWeight: 'bold'}}>GitHub URL</label>
                            <input name="github_link" value={formData.github_link} onChange={handleChange} placeholder="https://github.com/..." />
                        </div>

                        {/* Security Section */}
                        <div style={{marginTop: '30px', background: '#f8d7da', padding: '15px', borderRadius: '8px'}}>
                            <h4 style={{color: '#721c24', margin: '0 0 10px 0'}}>Security (Optional)</h4>
                            <label style={{fontSize: '0.9rem', fontWeight: 'bold', color: '#721c24'}}>Change Password</label>
                            <input 
                                type="password" 
                                name="password" 
                                value={formData.password || ''} 
                                onChange={handleChange} 
                                placeholder="Leave empty to keep current password"
                                style={{marginBottom: 0, borderColor: '#f5c6cb'}}
                            />
                        </div>

                        <div style={{marginTop: '25px', textAlign: 'right'}}>
                            <button type="submit" style={{padding: '10px 30px', fontSize: '1rem'}}>
                                Save Changes
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </>
    );
};

export default Settings;