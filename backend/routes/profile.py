from flask import Blueprint, request, jsonify
from extensions import db, bcrypt
from models.models import User, followers, Notification
from utils.decorators import token_required
from utils.file_utils import save_file # Import the file saver

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/me', methods=['GET'])
@token_required
def get_my_profile(current_user):
    return jsonify({
        'id': current_user.id,
        'firstname': current_user.firstname,
        'lastname': current_user.lastname,
        'email': current_user.email,
        'role': current_user.role,
        'bio': current_user.bio,
        'study_place': current_user.study_place,
        'work_place': current_user.work_place,
        'linkedin': current_user.linkedin_link,
        'github': current_user.github_link,
        'profile_pic': current_user.profile_pic, # <--- Sending the picture filename
        'followers_count': current_user.followers.count(),
        'following_count': current_user.followed.count()
    })

# NEW: Route to Upload Profile Picture
@profile_bp.route('/upload_pfp', methods=['POST'])
@token_required
def upload_pfp(current_user):
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
        
    filename = save_file(file)
    if filename:
        current_user.profile_pic = filename
        db.session.commit()
        return jsonify({'message': 'Profile picture updated', 'profile_pic': filename})
    
    return jsonify({'message': 'File upload failed'}), 500

@profile_bp.route('/update', methods=['PUT'])
@token_required
def update_settings(current_user):
    data = request.get_json()
    if 'firstname' in data: current_user.firstname = data['firstname']
    if 'lastname' in data: current_user.lastname = data['lastname']
    if 'bio' in data: current_user.bio = data['bio']
    if 'study_place' in data: current_user.study_place = data['study_place']
    if 'work_place' in data: current_user.work_place = data['work_place']
    if 'linkedin_link' in data: current_user.linkedin_link = data['linkedin_link']
    if 'github_link' in data: current_user.github_link = data['github_link']
    
    if 'password' in data and data['password']:
        hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        current_user.password = hashed_pw

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})

@profile_bp.route('/follow/<int:user_id>', methods=['POST'])
@token_required
def follow_user(current_user, user_id):
    user_to_follow = User.query.get_or_404(user_id)
    if user_to_follow.id == current_user.id:
        return jsonify({'message': 'You cannot follow yourself'}), 400

    is_following = db.session.query(followers).filter_by(
        follower_id=current_user.id, 
        followed_id=user_to_follow.id
    ).first() is not None

    if is_following:
        current_user.followed.remove(user_to_follow)
        msg = f"Unfollowed {user_to_follow.firstname}"
    else:
        current_user.followed.append(user_to_follow)
        msg = f"Followed {user_to_follow.firstname}"
        notif = Notification(
            message="started following you",
            user_id=user_to_follow.id,
            actor_id=current_user.id
        )
        db.session.add(notif)
        
    db.session.commit()
    return jsonify({'message': msg})

@profile_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user_profile(current_user, user_id):
    user = User.query.get_or_404(user_id)
    is_following = db.session.query(followers).filter_by(
        follower_id=current_user.id, 
        followed_id=user.id
    ).first() is not None

    return jsonify({
        'id': user.id,
        'firstname': user.firstname,
        'lastname': user.lastname,
        'role': user.role,
        'bio': user.bio,
        'study_place': user.study_place,
        'work_place': user.work_place,
        'profile_pic': user.profile_pic, # <--- Sending the picture filename
        'followers_count': user.followers.count(),
        'following_count': user.followed.count(),
        'is_following': is_following
    })