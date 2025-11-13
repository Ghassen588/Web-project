from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, jsonify
)
from extensions import db, bcrypt
from models import User, Post, Comment, Job, Application, UserRole, ApplicationStatus, Notification, NotificationType
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity,
    set_access_cookies, unset_jwt_cookies
)
from models import db, User, Job, Application, JobRating, UserRole
from datetime import datetime

main = Blueprint('main', __name__)

def get_current_user():
    user_id = get_jwt_identity()
    if user_id:
        return User.query.get(user_id)
    return None


def create_notification(recipient_id, sender_id, notification_type, post_id=None, comment_id=None, job_id=None, application_id=None):
    """Helper function to create notifications"""
    notification = Notification(
        recipient_id=recipient_id,
        sender_id=sender_id,
        notification_type=notification_type,
        post_id=post_id,
        comment_id=comment_id,
        job_id=job_id,
        application_id=application_id
    )
    db.session.add(notification)
    db.session.commit()


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')

        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return redirect(url_for('main.signup'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Un compte existe déjà avec cet email.', 'danger')
            return redirect(url_for('main.signup'))

        if role not in ['student', 'recruiter']:
            flash('Rôle invalide.', 'danger')
            return redirect(url_for('main.signup'))

        user_role = UserRole.STUDENT if role == 'student' else UserRole.RECRUITER

        new_user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            role=user_role
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()

            access_token = create_access_token(identity=new_user.id)
            response = redirect(url_for('main.forum'))
            set_access_cookies(response, access_token)

            flash('Compte créé avec succès !', 'success')
            return response
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création du compte: {e}', 'danger')

    return render_template('signup.html')


@main.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            response = redirect(url_for('main.forum'))
            set_access_cookies(response, access_token)
            flash('Connexion réussie !', 'success')
            return response
        else:
            flash('Email ou mot de passe incorrect.', 'danger')

    return render_template('signin.html')


@main.route('/logout')
@jwt_required()
def logout():
    response = redirect(url_for('main.index'))
    unset_jwt_cookies(response)
    flash('Vous avez été déconnecté.', 'info')
    return response


@main.route('/forum', methods=['GET', 'POST'])
@jwt_required()
def forum():
    user = get_current_user()

    # Create new post
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if content:
            new_post = Post(content=content, user_id=user.id)
            db.session.add(new_post)
            db.session.commit()
            flash('Post publié avec succès !', 'success')
            return redirect(url_for('main.forum'))
        else:
            flash('Le contenu du post ne peut pas être vide.', 'danger')

    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('forum.html', posts=posts, user=user)


# ---------- LIKE POST ----------
@main.route('/forum/like/<int:post_id>', methods=['POST'])
@jwt_required()
def like_post(post_id):
    user = get_current_user()
    post = Post.query.get_or_404(post_id)

    if user in post.liked_by:
        post.liked_by.remove(user)  # Unlike
    else:
        post.liked_by.append(user)  # Like
        # Create notification only if liking (not unliking)
        if user.id != post.author.id:  # Don't notify if liking own post
            create_notification(
                recipient_id=post.author.id,
                sender_id=user.id,
                notification_type=NotificationType.POST_LIKE,
                post_id=post_id
            )

    db.session.commit()
    return redirect(url_for('main.forum'))


# ---------- COMMENT POST ----------
@main.route('/forum/comment/<int:post_id>', methods=['POST'])
@jwt_required()
def comment_post(post_id):
    user = get_current_user()
    post = Post.query.get_or_404(post_id)
    content = request.form.get('comment', '').strip()

    if content:
        new_comment = Comment(content=content, user_id=user.id, post_id=post.id)
        db.session.add(new_comment)
        db.session.commit()
        
        # Create notification
        if user.id != post.author.id:  # Don't notify if commenting on own post
            create_notification(
                recipient_id=post.author.id,
                sender_id=user.id,
                notification_type=NotificationType.POST_COMMENT,
                post_id=post_id,
                comment_id=new_comment.id
            )
        
        flash('Commentaire ajouté avec succès.', 'success')
    else:
        flash('Le commentaire ne peut pas être vide.', 'danger')

    return redirect(url_for('main.forum'))





@main.route('/jobs', methods=['GET', 'POST'])
@jwt_required()
def jobs():
    user = get_current_user()

    # 🧱 Recruiter posting a new job
    if request.method == 'POST':
        if user.role != UserRole.RECRUITER:
            flash("Seuls les recruteurs peuvent publier une offre.", "danger")
            return redirect(url_for('main.jobs'))

        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        salary = request.form.get('salary', '').strip()
        is_remote = bool(request.form.get('is_remote'))
        location = request.form.get('location', '').strip()

        if not title or not description:
            flash("Le titre et la description sont obligatoires.", "danger")
            return redirect(url_for('main.jobs'))

        new_job = Job(
            title=title,
            description=description,
            salary=salary or None,
            is_remote=is_remote,
            location=location or None,
            recruiter_id=user.id,
            timestamp=datetime.now()
        )
        db.session.add(new_job)
        db.session.commit()
        flash("Offre publiée avec succès !", "success")
        return redirect(url_for('main.jobs'))

    # 🧭 Everyone can see job list
    jobs = Job.query.order_by(Job.timestamp.desc()).all()
    return render_template('jobs.html', jobs=jobs, user=user)


# ------------------- APPLY TO A JOB -------------------
@main.route('/jobs/apply/<int:job_id>', methods=['POST'])
@jwt_required()
def apply_job(job_id):
    user = get_current_user()
    job = Job.query.get_or_404(job_id)

    if user.role == UserRole.RECRUITER:
        flash("Les recruteurs ne peuvent pas postuler à des offres.", "danger")
        return redirect(url_for('main.jobs'))

    existing_application = job.applications.filter_by(user_id=user.id).first()
    if existing_application:
        flash("Vous avez déjà postulé à cette offre.", "info")
        return redirect(url_for('main.jobs'))

    new_application = Application(user_id=user.id, job_id=job.id)
    db.session.add(new_application)
    db.session.commit()
    
    # Create notification for recruiter
    create_notification(
        recipient_id=job.recruiter_id,
        sender_id=user.id,
        notification_type=NotificationType.JOB_APPLICATION,
        job_id=job_id,
        application_id=new_application.id
    )
    
    flash("Candidature envoyée avec succès !", "success")
    return redirect(url_for('main.jobs'))


# ------------------- RATE A JOB -------------------
@main.route('/jobs/rate/<int:job_id>', methods=['POST'])
@jwt_required()
def rate_job(job_id):
    user = get_current_user()
    job = Job.query.get_or_404(job_id)
    stars = int(request.form.get('stars', 0))

    if stars < 0 or stars > 5:
        flash("La note doit être entre 0 et 5.", "danger")
        return redirect(url_for('main.jobs'))

    rating = JobRating.query.filter_by(user_id=user.id, job_id=job.id).first()
    if rating:
        rating.stars = stars
    else:
        rating = JobRating(user_id=user.id, job_id=job.id, stars=stars)
        db.session.add(rating)
    db.session.commit()
    flash("Votre note a été enregistrée.", "success")
    return redirect(url_for('main.jobs'))


@main.route('/applications')
@jwt_required()
def applications():
    user = get_current_user()
    if user.role == UserRole.STUDENT:
        apps = Application.query.filter_by(user_id=user.id).order_by(Application.timestamp.desc()).all()
    else:
        apps = Application.query.join(Job).filter(Job.recruiter_id == user.id).order_by(Application.timestamp.desc()).all()
    return render_template('applications.html', applications=apps, user=user)


@main.route('/myprofile')
@jwt_required()
def my_profile():
    user = get_current_user()
    return render_template('profile.html', user=user, current_user=user)


@main.route('/profile/<int:user_id>')
@jwt_required()
def profile(user_id):
    user = User.query.get_or_404(user_id)
    current_user = get_current_user()
    return render_template('profile.html', user=user, current_user=current_user)


@main.route('/settings', methods=['GET', 'POST'])
@jwt_required()
def settings():
    user = get_current_user()

    if request.method == 'POST':
        user.email = request.form.get('email', user.email)
        user.bio = request.form.get('bio', user.bio)
        user.study_place = request.form.get('study_place', user.study_place)
        user.work_place = request.form.get('work_place', user.work_place)
        user.linkedin_link = request.form.get('linkedin_link', user.linkedin_link)
        user.github_link = request.form.get('github_link', user.github_link)

        try:
            db.session.commit()
            flash('Paramètres mis à jour.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {e}', 'danger')

        return redirect(url_for('main.settings'))

    return render_template('settings.html', user=user)


# ------------------- FOLLOW/UNFOLLOW USER -------------------
@main.route('/follow/<int:user_id>', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    current_user = get_current_user()
    user_to_follow = User.query.get_or_404(user_id)

    if current_user.id == user_id:
        flash("Vous ne pouvez pas vous suivre vous-même.", "danger")
        return redirect(url_for('main.profile', user_id=user_id))

    if user_to_follow in current_user.following:
        current_user.following.remove(user_to_follow)
        flash(f"Vous ne suivez plus {user_to_follow.firstname} {user_to_follow.lastname}.", "info")
    else:
        current_user.following.append(user_to_follow)
        db.session.commit()
        # Create notification only when following
        create_notification(
            recipient_id=user_to_follow.id,
            sender_id=current_user.id,
            notification_type=NotificationType.FOLLOW
        )
        flash(f"Vous suivez maintenant {user_to_follow.firstname} {user_to_follow.lastname}.", "success")

    db.session.commit()
    return redirect(url_for('main.profile', user_id=user_id))


# ------------------- SEARCH -------------------
@main.route('/search', methods=['GET'])
@jwt_required()
def search():
    current_user = get_current_user()
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')  # 'all', 'users', 'jobs'
    
    users_results = []
    jobs_results = []

    if query:
        # Search for users
        if search_type in ['all', 'users']:
            users_results = User.query.filter(
                (User.firstname.ilike(f'%{query}%')) | 
                (User.lastname.ilike(f'%{query}%')) |
                (User.email.ilike(f'%{query}%'))
            ).all()

        # Search for jobs
        if search_type in ['all', 'jobs']:
            jobs_results = Job.query.filter(
                (Job.title.ilike(f'%{query}%')) | 
                (Job.description.ilike(f'%{query}%'))
            ).all()

    return render_template('search.html', query=query, users=users_results, jobs=jobs_results, 
                         search_type=search_type, current_user=current_user)


# ------------------- NOTIFICATIONS -------------------
@main.route('/notifications')
@jwt_required()
def notifications():
    user = get_current_user()
    user_notifications = Notification.query.filter_by(recipient_id=user.id).order_by(Notification.timestamp.desc()).all()
    
    # Mark as read when viewing
    for notif in user_notifications:
        if not notif.is_read:
            notif.is_read = True
    db.session.commit()
    
    return render_template('notifications.html', notifications=user_notifications, user=user)


# ------------------- ACCEPT/REJECT APPLICATION -------------------
@main.route('/application/<int:app_id>/accept', methods=['POST'])
@jwt_required()
def accept_application(app_id):
    user = get_current_user()
    application = Application.query.get_or_404(app_id)

    if user.role != UserRole.RECRUITER or application.job.recruiter_id != user.id:
        flash("Vous n'êtes pas autorisé à accepter cette candidature.", "danger")
        return redirect(url_for('main.applications'))

    application.status = ApplicationStatus.ACCEPTED
    db.session.commit()
    
    # Create notification for student
    create_notification(
        recipient_id=application.student.id,
        sender_id=user.id,
        notification_type=NotificationType.APPLICATION_ACCEPTED,
        job_id=application.job_id,
        application_id=app_id
    )
    
    flash(f"Candidature de {application.student.firstname} {application.student.lastname} acceptée.", "success")
    return redirect(url_for('main.applications'))


@main.route('/application/<int:app_id>/refuse', methods=['POST'])
@jwt_required()
def refuse_application(app_id):
    user = get_current_user()
    application = Application.query.get_or_404(app_id)

    if user.role != UserRole.RECRUITER or application.job.recruiter_id != user.id:
        flash("Vous n'êtes pas autorisé à refuser cette candidature.", "danger")
        return redirect(url_for('main.applications'))

    application.status = ApplicationStatus.REFUSED
    db.session.commit()
    
    # Create notification for student
    create_notification(
        recipient_id=application.student.id,
        sender_id=user.id,
        notification_type=NotificationType.APPLICATION_REFUSED,
        job_id=application.job_id,
        application_id=app_id
    )
    
    flash(f"Candidature de {application.student.firstname} {application.student.lastname} refusée.", "info")
    return redirect(url_for('main.applications'))
