from flask import Blueprint, request, jsonify
from extensions import db
from models.models import Post, User, Comment, Notification, followers
from utils.decorators import token_required
from utils.file_utils import save_file

forum_bp = Blueprint('forum', __name__)

@forum_bp.route('/', methods=['GET'])
@token_required
def get_posts(current_user):
    filter_type = request.args.get('filter')
    
    if filter_type == 'following':
        followed_users = db.session.query(followers.c.followed_id).filter(followers.c.follower_id == current_user.id).all()
        followed_ids = [u[0] for u in followed_users]
        followed_ids.append(current_user.id)
        posts = Post.query.filter(Post.user_id.in_(followed_ids)).order_by(Post.date_posted.desc()).all()
    else:
        posts = Post.query.order_by(Post.date_posted.desc()).all()

    output = []
    for p in posts:
        is_pdf = p.image_url.lower().endswith('.pdf') if p.image_url else False
        output.append({
            'id': p.id,
            'content': p.content,
            'image_url': p.image_url,
            'is_pdf': is_pdf,
            'author': f"{p.author.firstname} {p.author.lastname}",
            'author_id': p.author.id, # Send ID
            'author_pic': p.author.profile_pic,
            'date': p.date_posted.strftime("%d %b %Y"),
            'likes': len(p.likes),
            'comments': [{
                'author': f"{c.author.firstname} {c.author.lastname}",
                'author_id': c.author.id, # Send ID
                'content': c.content
            } for c in p.comments]
        })
    return jsonify(output)

@forum_bp.route('/create', methods=['POST'])
@token_required
def create_post(current_user):
    content = request.form.get('content')
    file = request.files.get('file')
    image_filename = save_file(file) if file else None

    new_post = Post(content=content, image_url=image_filename, user_id=current_user.id)
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message': 'Post created!'}), 201

@forum_bp.route('/<int:post_id>/like', methods=['POST'])
@token_required
def like_post(current_user, post_id):
    post = Post.query.get_or_404(post_id)
    if current_user in post.likes:
        post.likes.remove(current_user)
    else:
        post.likes.append(current_user)
        if post.author != current_user:
            notif = Notification(
                message="liked your post",
                user_id=post.user_id,
                actor_id=current_user.id # Save Actor
            )
            db.session.add(notif)
    db.session.commit()
    return jsonify({'message': 'Success'})

@forum_bp.route('/<int:post_id>/comment', methods=['POST'])
@token_required
def add_comment(current_user, post_id):
    data = request.get_json()
    post = Post.query.get_or_404(post_id)
    new_comment = Comment(content=data['content'], user_id=current_user.id, post_id=post.id)
    db.session.add(new_comment)
    
    if post.author != current_user:
        notif = Notification(
            message="commented on your post",
            user_id=post.user_id,
            actor_id=current_user.id # Save Actor
        )
        db.session.add(notif)
        
    db.session.commit()
    return jsonify({'message': 'Comment added'})