from flask import Blueprint, jsonify
from extensions import db
from models.models import Notification
from utils.decorators import token_required

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
@token_required
def get_notifications(current_user):
    notifs = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).all()
    
    results = []
    for n in notifs:
        actor_name = "Someone"
        actor_id = None
        if n.actor:
            actor_name = f"{n.actor.firstname} {n.actor.lastname}"
            actor_id = n.actor.id

        results.append({
            'id': n.id,
            'message': n.message,
            'actor_name': actor_name,
            'actor_id': actor_id,
            'is_read': n.is_read,
            'date': n.created_at.strftime("%Y-%m-%d %H:%M")
        })
        
        if not n.is_read: n.is_read = True
            
    db.session.commit()
    return jsonify(results)