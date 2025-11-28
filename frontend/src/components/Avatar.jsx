import React from 'react';

const Avatar = ({ name = "", size = "50px", fontSize = "1.2rem" ,image = null}) => {
    const hasImage = image && image !== 'default.jpg';
    
    if (hasImage) {
        return (
            <img 
                src={`http://localhost:5000/static/uploads/${image}`}
                alt={name}
                style={{
                    width: size,
                    height: size,
                    borderRadius: '50%',
                    objectFit: 'cover',
                    border: '2px solid white',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    backgroundColor: '#fff'
                }}
            />
        );
    }
    
    const initials = name
        .split(' ')
        .map(word => word[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
    

    return (
        <div style={{
            width: size,
            height: size,
            borderRadius: '50%',
            backgroundColor: '#0a66c2', // LinkedIn Blue
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            fontSize: fontSize,
            border: '2px solid white',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
            {initials}
        </div>
    );
};

export default Avatar;