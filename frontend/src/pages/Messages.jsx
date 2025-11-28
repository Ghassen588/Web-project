import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom'; // <--- NEW IMPORT
import TopNavigation from '../components/TopNavigation';
import Avatar from '../components/Avatar';
import api from '../api/config';

const Messages = () => {
    const [searchParams] = useSearchParams(); // <--- HOOK TO READ URL
    const [conversations, setConversations] = useState([]);
    const [activeChat, setActiveChat] = useState(null); 
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState("");

    // 1. Load Conversations on Mount
    useEffect(() => {
        loadConversations();
    }, []);

    // 2. NEW: Listener for URL changes (e.g., coming from Profile)
    useEffect(() => {
        const uid = searchParams.get('uid'); // Get ?uid=...
        if (uid && conversations.length >= 0) {
            initDirectChat(uid);
        }
    }, [searchParams, conversations]); // Run when URL or Conversation list changes

    // 3. LOGIC: Find user or fetch their details if new
    const initDirectChat = async (uid) => {
        const targetId = parseInt(uid);
        
        // A. Do we already have a chat open with them?
        const existing = conversations.find(c => c.id === targetId);
        if (existing) {
            setActiveChat(existing);
        } else {
            // B. If NO, we need to fetch their name/pic to show the empty chat window
            try {
                // We reuse the profile endpoint to get their details
                const res = await api.get(`/profile/${targetId}`);
                const user = res.data;
                
                // Create a "Temporary" chat object
                setActiveChat({
                    id: user.id,
                    name: `${user.firstname} ${user.lastname}`,
                    pic: user.profile_pic,
                    last_msg: 'New conversation', 
                    timestamp: ''
                });
            } catch (err) {
                console.error("Could not load user details for chat", err);
            }
        }
    };

    // 4. Load Messages when Active Chat changes
    useEffect(() => {
        if (activeChat) {
            loadMessages(activeChat.id);
            // Poll for new messages every 3 seconds
            const interval = setInterval(() => loadMessages(activeChat.id), 3000);
            return () => clearInterval(interval);
        }
    }, [activeChat]);

    const loadConversations = async () => {
        try {
            const res = await api.get('/messages/conversations');
            setConversations(res.data);
        } catch(err) { console.error(err); }
    };

    const loadMessages = async (userId) => {
        try {
            const res = await api.get(`/messages/${userId}`);
            setMessages(res.data);
        } catch(err) { console.error(err); }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!inputText.trim() || !activeChat) return;

        try {
            await api.post('/messages/send', {
                recipient_id: activeChat.id,
                body: inputText
            });
            setInputText("");
            loadMessages(activeChat.id);
            loadConversations(); // Update sidebar to show the new msg
        } catch(err) { alert('Failed to send'); }
    };

    const handleLike = async (msgId) => {
        try {
            await api.post(`/messages/${msgId}/like`);
            loadMessages(activeChat.id); 
        } catch(err) { console.error(err); }
    };

    return (
        <>
            <TopNavigation />
            <div className="page-container" style={{display: 'flex', height: '80vh', gap: '20px', marginTop: '20px'}}>
                
                {/* SIDEBAR */}
                <div className="card" style={{width: '300px', padding: '0', display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>
                    <h3 style={{padding: '15px', borderBottom: '1px solid #eee', margin: 0, background: '#f9fafb'}}>Messaging</h3>
                    <div style={{overflowY: 'auto', flex: 1}}>
                        {conversations.length === 0 && <p style={{padding: '15px', color: '#666'}}>No conversations yet.</p>}
                        {conversations.map(contact => (
                            <div 
                                key={contact.id}
                                onClick={() => setActiveChat(contact)}
                                style={{
                                    display: 'flex', gap: '10px', padding: '15px', 
                                    cursor: 'pointer', borderBottom: '1px solid #f3f3f3',
                                    background: activeChat?.id === contact.id ? '#eef3f8' : 'white'
                                }}
                            >
                                <Avatar name={contact.name} image={contact.pic} size="40px" />
                                <div style={{overflow: 'hidden'}}>
                                    <div style={{fontWeight: 'bold', fontSize: '0.9rem'}}>{contact.name}</div>
                                    <div style={{fontSize: '0.8rem', color: '#666', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>
                                        {contact.last_msg}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* CHAT WINDOW */}
                <div className="card" style={{flex: 1, padding: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>
                    {activeChat ? (
                        <>
                            <div style={{padding: '10px 15px', borderBottom: '1px solid #eee', background: '#f9fafb', display: 'flex', alignItems: 'center', gap: '10px'}}>
                                <Avatar name={activeChat.name} image={activeChat.pic} size="32px" />
                                <strong>{activeChat.name}</strong>
                            </div>

                            <div style={{flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px', background: '#fff'}}>
                                {messages.map(msg => (
                                    <div key={msg.id} style={{alignSelf: msg.is_me ? 'flex-end' : 'flex-start', maxWidth: '70%'}}>
                                        <div style={{
                                            background: msg.is_me ? '#0a66c2' : '#e9e9eb',
                                            color: msg.is_me ? 'white' : 'black',
                                            padding: '10px 15px', borderRadius: '16px', position: 'relative'
                                        }}>
                                            {msg.body}
                                            {msg.is_liked && <div style={{position: 'absolute', bottom: '-10px', right: '-5px', fontSize: '1.2rem'}}>❤️</div>}
                                        </div>
                                        <div style={{fontSize: '0.7rem', color: '#999', marginTop: '5px', textAlign: msg.is_me ? 'right' : 'left'}}>
                                            {msg.timestamp}
                                            {!msg.is_me && !msg.is_liked && <span onClick={() => handleLike(msg.id)} style={{cursor: 'pointer', marginLeft: '5px'}}>♡</span>}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <form onSubmit={handleSend} style={{padding: '15px', borderTop: '1px solid #eee', display: 'flex', gap: '10px', background: '#f9fafb'}}>
                                <input value={inputText} onChange={(e) => setInputText(e.target.value)} placeholder="Write a message..." style={{marginBottom: 0, borderRadius: '20px'}} />
                                <button type="submit" style={{width: 'auto', borderRadius: '20px', padding: '0 20px'}}>Send</button>
                            </form>
                        </>
                    ) : (
                        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#666'}}>
                            Select a conversation or visit a profile to message.
                        </div>
                    )}
                </div>
            </div>
        </>
    );
};

export default Messages;