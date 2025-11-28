import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import TopNavigation from '../components/TopNavigation';
import Avatar from '../components/Avatar';
import api from '../api/config';

const UserProfile = () => {
    const { id } = useParams();
    const [user, setUser] = useState(null);

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const res = await api.get(`/profile/${id}`);
                setUser(res.data);
            } catch (err) {
                console.error("Error fetching user", err);
            }
        };
        fetchUser();
    }, [id]);

    const handleFollow = async () => {
        try {
            await api.post(`/profile/follow/${id}`);
            // Refresh data to update button
            const res = await api.get(`/profile/${id}`);
            setUser(res.data);
        } catch (err) {
            alert('Action failed');
        }
    };

    if (!user) return <div className="page-container">Loading...</div>;

    return (
        <>
            <TopNavigation />
            <div className="page-container profile-page">
                {/* Profile Header Card */}
                <div className="card profile-header">
                    <div style={{display: 'flex', justifyContent: 'center', marginBottom: '15px'}}>
                        <Avatar 
                            name={`${user.firstname} ${user.lastname}`} 
                            image={user.profile_pic} 
                            size="120px" 
                            fontSize="2.5rem" 
                        />
                    </div>
                    
                    <h2 style={{marginBottom: '5px'}}>{user.firstname} {user.lastname}</h2>
                    <span className="badge">{user.role}</span>
                    <p style={{marginTop: '15px', color: '#666', maxWidth: '500px', margin: '15px auto'}}>{user.bio || "No bio available."}</p>
                    
                    <div className="stats-row" style={{display: 'flex', gap: '30px', justifyContent: 'center', margin: '20px 0', padding: '15px 0'}}>
                        <div style={{textAlign: 'center'}}>
                            <div style={{fontWeight: 'bold', fontSize: '1.2rem'}}>{user.followers_count}</div>
                            <small>Followers</small>
                        </div>
                        <div style={{textAlign: 'center'}}>
                            <div style={{fontWeight: 'bold', fontSize: '1.2rem'}}>{user.following_count}</div>
                            <small>Following</small>
                        </div>
                    </div>

                    <div style={{display: 'flex', gap: '10px', justifyContent: 'center'}}>
                        <button 
                            onClick={handleFollow} 
                            style={{
                                backgroundColor: user.is_following ? 'white' : '#0a66c2',
                                color: user.is_following ? '#666' : 'white',
                                border: user.is_following ? '1px solid #ccc' : 'none',
                                width: '150px'
                            }}
                        >
                            {user.is_following ? '✅ Following' : '+ Follow'}
                        </button>
                        
                        <Link 
                            to={`/messages?uid=${user.id}`}
                            style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                backgroundColor: 'white',
                                color: '#666',
                                border: '1px solid #ccc',
                                width: '150px',
                                borderRadius: '24px',
                                textDecoration: 'none',
                                fontWeight: 'bold',
                                fontSize: '14px'
                            }}
                        >
                            ✉️ Message
                        </Link>
                    </div>
                </div>

                {/* Info Card */}
                <div className="card">
                    <h3 style={{borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '15px'}}>Professional Info</h3>
                    <div style={{display: 'grid', gap: '15px'}}>
                        <div><strong>🎓 Education:</strong> {user.study_place || "N/A"}</div>
                        <div><strong>💼 Work:</strong> {user.work_place || "N/A"}</div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default UserProfile;