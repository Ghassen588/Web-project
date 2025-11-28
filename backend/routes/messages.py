from flask import Blueprint, request, jsonify
from extensions import db
from models.models import Message, User
from utils.decorators import token_required
from sqlalchemy import or_, and_, desc

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/conversations', methods=['GET'])
@token_required
def get_conversations(current_user):
    # This query finds all unique users you have exchanged messages with
    # It's a bit complex in SQL, so we fetch distinct IDs
    sent_ids = db.session.query(Message.recipient_id).filter_by(sender_id=current_user.id).distinct()
    received_ids = db.session.query(Message.sender_id).filter_by(recipient_id=current_user.id).distinct()
    
    # Combine sets of IDs
    all_contact_ids = set([r[0] for r in sent_ids] + [r[0] for r in received_ids])
    
    contacts = []
    for user_id in all_contact_ids:
        user = User.query.get(user_id)
        if user:
            # Get last message for preview
            last_msg = Message.query.filter(
                or_(
                    and_(Message.sender_id == current_user.id, Message.recipient_id == user.id),
                    and_(Message.sender_id == user.id, Message.recipient_id == current_user.id)
                )
            ).order_by(Message.timestamp.desc()).first()
            
            contacts.append({
                'id': user.id,
                'name': f"{user.firstname} {user.lastname}",
                'pic': user.profile_pic,
                'last_msg': last_msg.body if last_msg else "",
                'timestamp': last_msg.timestamp.strftime("%H:%M") if last_msg else ""
            })
            
    return jsonify(contacts)

@messages_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_chat_history(current_user, user_id):
    # Fetch conversation between Me and user_id
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.recipient_id == user_id),
            and_(Message.sender_id == user_id, Message.recipient_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).all()
    
    output = []
    for m in messages:
        output.append({
            'id': m.id,
            'body': m.body,
            'timestamp': m.timestamp.strftime("%d %b %H:%M"),
            'sender_id': m.sender_id,
            'is_liked': m.is_liked,
            'is_me': m.sender_id == current_user.id
        })
    return jsonify(output)

@messages_bp.route('/send', methods=['POST'])
@token_required
def send_message(current_user):
    data = request.get_json()
    recipient_id = data.get('recipient_id')
    body = data.get('body')
    
    if not body or not recipient_id:
        return jsonify({'message': 'Missing data'}), 400
        
    new_msg = Message(
        body=body,
        sender_id=current_user.id,
        recipient_id=recipient_id
    )
    db.session.add(new_msg)
    db.session.commit()
    return jsonify({'message': 'Sent'})

@messages_bp.route('/<int:msg_id>/like', methods=['POST'])
@token_required
def like_message(current_user, msg_id):
    msg = Message.query.get_or_404(msg_id)
    
    # Only the recipient can like a message
    if msg.recipient_id != current_user.id:
        return jsonify({'message': 'Cannot like this message'}), 403
        
    msg.is_liked = not msg.is_liked # Toggle
    db.session.commit()
    return jsonify({'message': 'Like status updated', 'is_liked': msg.is_liked})