from flask import Blueprint, request, jsonify
from models.models import User, Job
from sqlalchemy import or_

search_bp = Blueprint('search', __name__)

@search_bp.route('/', methods=['GET'])
def search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all') # 'users', 'jobs', 'all'
    
    results = {'users': [], 'jobs': []}

    if not query:
        return jsonify(results)

    # Search Users
    if search_type in ['users', 'all']:
        users = User.query.filter(
            or_(
                User.firstname.ilike(f'%{query}%'),
                User.lastname.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        ).all()
        results['users'] = [{
            'id': u.id,
            'name': f"{u.firstname} {u.lastname}",
            'role': u.role,
            'avatar': u.profile_pic
        } for u in users]

    # Search Jobs
    if search_type in ['jobs', 'all']:
        jobs = Job.query.filter(
            or_(
                Job.title.ilike(f'%{query}%'),
                Job.description.ilike(f'%{query}%')
            )
        ).all()
        results['jobs'] = [{
            'id': j.id,
            'title': j.title,
            'company': f"{j.recruiter.firstname} {j.recruiter.lastname}",
            'location': j.location
        } for j in jobs]

    return jsonify(results)