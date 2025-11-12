import os
from flask import Flask, render_template, g
from config import Config
from extensions import db, bcrypt, jwt, migrate
from models import User, UserRole
from flask_jwt_extended import get_jwt_identity

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # disable JWT cookie CSRF

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.before_request
    def set_user_global():
        g.user = None

    @jwt.user_lookup_loader
    def user_lookup_callback(jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='student@test.com').first():
            student = User(firstname='Test', lastname='Student',
                           email='student@test.com', role=UserRole.STUDENT)
            student.set_password('password')
            db.session.add(student)
        if not User.query.filter_by(email='recruiter@test.com').first():
            recruiter = User(firstname='Test', lastname='Recruiter',
                             email='recruiter@test.com',
                             role=UserRole.RECRUITER, work_place="Tech Corp")
            recruiter.set_password('password')
            db.session.add(recruiter)
        db.session.commit()

    @app.context_processor
    def inject_user():
        try:
            user_id = get_jwt_identity()
            if user_id:
                return {'user': User.query.get(user_id)}
        except Exception:
            pass
        return {'user': None}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
