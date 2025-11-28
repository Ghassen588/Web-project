from flask import Blueprint, jsonify, request
from extensions import db
from models.models import Application, Job, Notification
from utils.decorators import token_required

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/', methods=['GET'])
@token_required
def get_applications(current_user):
    output = []
    
    if current_user.role == 'student':
        # Students see jobs they applied to
        apps = Application.query.filter_by(student_id=current_user.id).all()
        for app in apps:
            output.append({
                'id': app.id,
                'job_title': app.job.title,
                'company': f"{app.job.recruiter.firstname} {app.job.recruiter.lastname}",
                'status': app.status,
                'date': app.date_applied.strftime("%Y-%m-%d")
            })
            
    elif current_user.role == 'recruiter':
        # Recruiters see applications for their jobs
        # We join with Job table to filter by recruiter_id
        apps = db.session.query(Application)\
            .join(Job, Application.job_id == Job.id)\
            .filter(Job.recruiter_id == current_user.id)\
            .all()
            
        for app in apps:
            output.append({
                'id': app.id,
                'job_title': app.job.title,
                'applicant_name': f"{app.applicant.firstname} {app.applicant.lastname}",
                'applicant_id': app.applicant.id,
                'status': app.status,
                'date': app.date_applied.strftime("%Y-%m-%d")
            })
            
    return jsonify(output)

@applications_bp.route('/<int:app_id>/status', methods=['PUT'])
@token_required
def update_status(current_user, app_id):
    if current_user.role != 'recruiter':
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    new_status = data.get('status') # 'Accepted' or 'Refused'
    
    application = Application.query.get_or_404(app_id)
    
    # Security check: Ensure this job belongs to the recruiter
    if application.job.recruiter_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403

    application.status = new_status
    
    # Notify Student
    notif = Notification(
        message=f"Your application for {application.job.title} was {new_status}",
        user_id=application.applicant.id
    )
    db.session.add(notif)
    db.session.commit()
    
    return jsonify({'message': f'Application marked as {new_status}'})