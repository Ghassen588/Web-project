from flask import Blueprint, request, jsonify, make_response
from extensions import db, bcrypt
from models.models import User
import jwt
import datetime
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    new_user = User(
        firstname=data['firstname'],
        lastname=data['lastname'],
        email=data['email'],
        password=hashed_password,
        role=data['role']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully!'}), 201

@auth_bp.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        token = jwt.encode({
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'role': user.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, Config.SECRET_KEY, algorithm="HS256")

        response = make_response(jsonify({'message': 'Login successful', 'role': user.role}))
        # HTTPOnly cookie for security
        response.set_cookie('token', token, httponly=True, samesite='Lax') 
        return response

    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({'message': 'Logged out'}))
    response.set_cookie('token', '', expires=0)
    return response