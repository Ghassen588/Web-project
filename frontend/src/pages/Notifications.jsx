import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import TopNavigation from '../components/TopNavigation';
import Avatar from '../components/Avatar';
import api from '../api/config';

const Notifications = () => {
    const [notifs, setNotifs] = useState([]);

    useEffect(() => {
        const fetchNotifs = async () => {
            try {
                const res = await api.get('/notifications/');
                setNotifs(res.data);
            } catch (err) { console.error(err); }
        };
        fetchNotifs();
    }, []);

    return (
        <>
            <TopNavigation />
            <div className="page-container" style={{maxWidth: '800px'}}>
                <h2>Notifications</h2>
                <div className="notif-list">
                    {notifs.length === 0 ? (
                        <div className="card" style={{textAlign: 'center', padding: '30px'}}>No new notifications.</div>
                    ) : (
                        notifs.map(n => (
                            <div key={n.id} className="card" style={{display: 'flex', gap: '15px', alignItems: 'center', borderLeft: n.is_read ? '1px solid #e0e0e0' : '4px solid #0a66c2', backgroundColor: n.is_read ? 'white' : '#eef3f8'}}>
                                <Link to={n.actor_id ? `/user/${n.actor_id}` : '#'}>
                                    {n.actor_id ? <Avatar name={n.actor_name} size="40px" fontSize="1rem" /> : <div style={{width:'40px', height:'40px', background:'#0a66c2', borderRadius:'50%', display:'flex', alignItems:'center', justifyContent:'center', color:'white'}}>📣</div>}
                                </Link>
                                <div style={{flex: 1}}>
                                    <p style={{margin: '0 0 5px 0'}}>
                                        {n.actor_id ? (
                                            <Link to={`/user/${n.actor_id}`} style={{fontWeight: 'bold', color: '#0a66c2', textDecoration: 'none'}}>
                                                {n.actor_name}
                                            </Link>
                                        ) : <strong>System</strong>}
                                        {" " + n.message}
                                    </p>
                                    <small style={{color: '#666'}}>{n.date}</small>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </>
    );
};
export default Notifications;