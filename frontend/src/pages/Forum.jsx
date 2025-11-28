import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import TopNavigation from '../components/TopNavigation';
import Avatar from '../components/Avatar';
import api from '../api/config';

const Forum = () => {
    const [posts, setPosts] = useState([]);
    const [filter, setFilter] = useState('all');
    const [newPostContent, setNewPostContent] = useState('');
    const [file, setFile] = useState(null);

    const loadPosts = async () => {
        try {
            const res = await api.get(`/forum/?filter=${filter}`);
            setPosts(res.data);
        } catch (err) { console.error(err); }
    };

    useEffect(() => { loadPosts(); }, [filter]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('content', newPostContent);
        if (file) formData.append('file', file);
        await api.post('/forum/create', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
        setNewPostContent('');
        setFile(null);
        loadPosts();
    };

    const handleLike = async (postId) => {
        await api.post(`/forum/${postId}/like`);
        loadPosts();
    };

    return (
        <>
            <TopNavigation />
            <div className="page-container">
                <div className="card create-post-card">
                    <div style={{display: 'flex', gap: '15px', marginBottom: '10px'}}>
                        <Avatar name="Me" size="50px" /> 
                        <textarea placeholder="Share something..." value={newPostContent} onChange={(e) => setNewPostContent(e.target.value)} style={{resize: 'none', height: '80px'}} />
                    </div>
                    <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                        <input type="file" onChange={(e) => setFile(e.target.files[0])} style={{border: 'none', padding: 0, width: 'auto'}} />
                        <button onClick={handleSubmit} style={{width: 'auto'}}>Post</button>
                    </div>
                </div>

                <div style={{display: 'flex', gap: '10px', marginBottom: '20px'}}>
                    <button onClick={() => setFilter('all')} style={{background: filter === 'all' ? '#0a66c2' : 'white', color: filter === 'all' ? 'white' : '#666', border: '1px solid #ccc'}}>🌎 All Posts</button>
                    <button onClick={() => setFilter('following')} style={{background: filter === 'following' ? '#0a66c2' : 'white', color: filter === 'following' ? 'white' : '#666', border: '1px solid #ccc'}}>👥 Following</button>
                </div>

                <div className="feed">
                    {posts.map(post => (
                        <div key={post.id} className="card post-card">
                            <div className="post-header">
                                <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
                                    <Link to={`/user/${post.author_id}`}>
                                        <Avatar name={post.author} image={post.author_pic} size="48px" fontSize="1rem" />
                                    </Link>
                                    <div style={{display: 'flex', flexDirection: 'column'}}>
                                        <Link to={`/user/${post.author_id}`} style={{color: '#222', textDecoration: 'none'}}>
                                            <strong>{post.author}</strong>
                                        </Link>
                                        <small>{post.date}</small>
                                    </div>
                                </div>
                            </div>

                            <p style={{marginTop: '10px', whiteSpace: 'pre-wrap'}}>{post.content}</p>

                            {post.image_url && (
                                post.is_pdf ? (
                                    <div style={{background: '#f3f2ef', padding: '15px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '10px', marginTop: '10px', border: '1px solid #e0e0e0'}}>
                                        <span style={{fontSize: '2rem'}}>📄</span>
                                        <a href={`http://localhost:5000/static/uploads/${post.image_url}`} target="_blank" rel="noopener noreferrer" style={{textDecoration: 'underline', color: '#0a66c2'}}>View PDF</a>
                                    </div>
                                ) : (
                                    <img src={`http://localhost:5000/static/uploads/${post.image_url}`} alt="Post attachment" className="post-image" />
                                )
                            )}

                            <div className="post-actions">
                                <button onClick={() => handleLike(post.id)} className="secondary" style={{border: 'none', display: 'flex', alignItems: 'center', gap: '5px'}}>👍 Like ({post.likes})</button>
                                <button className="secondary" style={{border: 'none'}}>💬 Comment</button>
                            </div>

                            <div className="comments-section" style={{background: '#f9fafb', margin: '10px -16px -16px', padding: '15px', borderTop: '1px solid #eee'}}>
                                {post.comments && post.comments.length > 0 && (
                                    <div style={{marginBottom: '15px', display: 'flex', flexDirection: 'column', gap: '10px'}}>
                                        {post.comments.map((c, index) => (
                                            <div key={index} style={{display: 'flex', gap: '10px'}}>
                                                <Link to={`/user/${c.author_id}`}>
                                                    <Avatar name={c.author} size="32px" fontSize="0.7rem" />
                                                </Link>
                                                <div style={{background: '#f1f1f1', padding: '8px 12px', borderRadius: '0 12px 12px 12px'}}>
                                                    <Link to={`/user/${c.author_id}`} style={{color: '#222', textDecoration: 'none'}}>
                                                        <strong>{c.author}</strong>
                                                    </Link>
                                                    <div style={{fontSize: '0.9rem'}}>{c.content}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                                <div style={{display: 'flex', gap: '10px', alignItems: 'center'}}>
                                    <input type="text" placeholder="Add a comment..." id={`comment-input-${post.id}`} style={{marginBottom: 0, borderRadius: '20px', background: 'white'}} />
                                    <button onClick={async () => {
                                        const input = document.getElementById(`comment-input-${post.id}`);
                                        if(input.value) {
                                            await api.post(`/forum/${post.id}/comment`, {content: input.value});
                                            input.value = '';
                                            loadPosts(); 
                                        }
                                    }} style={{width: 'auto', borderRadius: '20px'}}>Send</button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </>
    );
};
export default Forum;