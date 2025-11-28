import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:5000',
    withCredentials: true, // IMPORTANT: Allows sending/receiving cookies
    headers: {
        'Content-Type': 'application/json',
    },
});

export default api;