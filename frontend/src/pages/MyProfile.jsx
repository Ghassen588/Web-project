import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import TopNavigation from '../components/TopNavigation';
import Avatar from '../components/Avatar';
import api from '../api/config';

const MyProfile = () => {
    const [user, setUser] = useState(null);

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        try {
            const res = await api.get('/profile/me');
            setUser(res.data);
        } catch (err) { console.error("Error fetching profile", err); }
    };

    const handleImageUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            await api.post('/profile/upload_pfp', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            // Reload profile to see changes
            loadProfile(); 
        } catch (err) {
            alert('Failed to upload image');
        }
    };

    if (!user) return <div className="page-container">Loading...</div>;

    return (
        <>
            <TopNavigation />
            <div className="page-container profile-page">
                {/* Profile Header Card */}
                <div className="card profile-header" style={{position: 'relative'}}>
                    
                    <div style={{display: 'flex', justifyContent: 'center', marginBottom: '15px', position: 'relative'}}>
                        {/* Pass the image to Avatar */}
                        <Avatar name={`${user.firstname} ${user.lastname}`} image={user.profile_pic} size="120px" fontSize="2.5rem" />
                        
                        {/* Hidden File Input + Label Overlay */}
                        <div style={{position: 'absolute', bottom: 0, marginLeft: '80px'}}>
                            <label htmlFor="pfp-upload" style={{
                                background: 'white', 
                                border: '1px solid #ccc', 
                                borderRadius: '50%', 
                                width: '32px', 
                                height: '32px', 
                                display: 'flex', 
                                alignItems: 'center', 
                                justifyContent: 'center', 
                                cursor: 'pointer',
                                boxShadow: '0 2px 5px rgba(0,0,0,0.2)'
                            }}>
                                📷
                            </label>
                            <input 
                                id="pfp-upload" 
                                type="file" 
                                onChange={handleImageUpload} 
                                style={{display: 'none'}} 
                                accept="image/*"
                            />
                        </div>
                    </div>
                    
                    <h2 style={{marginBottom: '5px'}}>{user.firstname} {user.lastname}</h2>
                    <span className="badge">{user.role}</span>
                    <p style={{marginTop: '15px', color: '#666', maxWidth: '500px', margin: '15px auto'}}>{user.bio || "No bio added yet."}</p>

                    <div className="stats-row" style={{display: 'flex', gap: '30px', justifyContent: 'center', margin: '20px 0', borderTop: '1px solid #eee', borderBottom: '1px solid #eee', padding: '15px 0'}}>
                        <div style={{textAlign: 'center'}}><div style={{fontWeight: 'bold', fontSize: '1.2rem'}}>{user.followers_count}</div><small>Followers</small></div>
                        <div style={{textAlign: 'center'}}><div style={{fontWeight: 'bold', fontSize: '1.2rem'}}>{user.following_count}</div><small>Following</small></div>
                    </div>

                    <Link to="/settings" style={{display: 'inline-block', padding: '8px 20px', border: '1px solid #0a66c2', borderRadius: '20px', color: '#0a66c2'}}>
                        ✏️ Edit Profile
                    </Link>
                </div>

                <div className="card">
                    <h3 style={{borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '15px'}}>Details</h3>
                    <div style={{display: 'grid', gap: '15px'}}>
                        <div><strong>🎓 Education:</strong> {user.study_place || "Not listed"}</div>
                        <div><strong>💼 Work:</strong> {user.work_place || "Not listed"}</div>
                        <div><strong>🔗 LinkedIn:</strong> {user.linkedin ? <a href={user.linkedin} target="_blank">View</a> : "-"}</div>
                        <div><strong>💻 GitHub:</strong> {user.github ? <a href={user.github} target="_blank">View</a> : "-"}</div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default MyProfile;