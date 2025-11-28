from flask import Blueprint, request, jsonify
from extensions import db
from models.models import Job, Application, JobRating, Notification
from utils.decorators import token_required

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/', methods=['GET'])
@token_required
def get_jobs(current_user):
    jobs = Job.query.all()
    output = []
    for job in jobs:
        # Check if current user saved this job
        is_saved = False
        # Handle the dynamic relationship safely
        if job in current_user.saved:
            is_saved = True
            
        output.append({
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'salary': job.salary,
            'location': job.location,
            'recruiter': f"{job.recruiter.firstname} {job.recruiter.lastname}",
            'rating': job.average_rating(),
            'is_saved': is_saved,   
            'recruiter_pic': job.recruiter.profile_pic,
        })
    return jsonify(output)

@jobs_bp.route('/create', methods=['POST'])
@token_required
def create_job(current_user):
    if current_user.role != 'recruiter':
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    new_job = Job(
        title=data['title'],
        description=data['description'],
        salary=data['salary'],
        location=data['location'],
        recruiter_id=current_user.id
    )
    db.session.add(new_job)
    db.session.commit()
    return jsonify({'message': 'Job created!'}), 201

@jobs_bp.route('/<int:job_id>/apply', methods=['POST'])
@token_required
def apply_job(current_user, job_id):
    if current_user.role != 'student':
        return jsonify({'message': 'Only students can apply'}), 403
        
    # Check if already applied
    existing = Application.query.filter_by(job_id=job_id, student_id=current_user.id).first()
    if existing:
        return jsonify({'message': 'Already applied'}), 400

    # 1. Create Application
    application = Application(job_id=job_id, student_id=current_user.id)
    db.session.add(application)
    
    # 2. Notify Recruiter (THIS WAS MISSING)
    job = Job.query.get(job_id)
    if job:
        notif = Notification(
            message=f"applied for {job.title}",
            user_id=job.recruiter_id,
            actor_id=current_user.id # Save Actor
        )
        db.session.add(notif)

    db.session.commit()
    return jsonify({'message': 'Applied successfully'}), 200

@jobs_bp.route('/<int:job_id>/save', methods=['POST'])
@token_required
def save_job(current_user, job_id):
    job = Job.query.get_or_404(job_id)
    if job in current_user.saved:
        current_user.saved.remove(job)
        msg = "Job removed from saved"
    else:
        current_user.saved.append(job)
        msg = "Job saved"
    db.session.commit()
    return jsonify({'message': msg})

@jobs_bp.route('/<int:job_id>/rate', methods=['POST'])
@token_required
def rate_job(current_user, job_id):
    data = request.get_json()
    stars = data.get('stars')
    
    if not stars or not (1 <= stars <= 5):
        return jsonify({'message': 'Invalid rating'}), 400

    existing_rating = JobRating.query.filter_by(user_id=current_user.id, job_id=job_id).first()
    if existing_rating:
        existing_rating.stars = stars
    else:
        new_rating = JobRating(user_id=current_user.id, job_id=job_id, stars=stars)
        db.session.add(new_rating)
    
    db.session.commit()
    return jsonify({'message': 'Rating submitted'})