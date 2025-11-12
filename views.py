from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, jsonify
)
from extensions import db, bcrypt
from models import User, Post, Comment, Job, Application, UserRole, ApplicationStatus
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
