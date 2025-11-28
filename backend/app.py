from flask import Flask
from config import Config
from extensions import db, bcrypt, cors
from routes.auth import auth_bp
from routes.jobs import jobs_bp
from routes.search import search_bp
from routes.forum import forum_bp
from routes.profile import profile_bp
from routes.notifications import notifications_bp
from routes.applications import applications_bp
from routes.messages import messages_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, supports_credentials=True, resources={r"/*": {"origins": Config.FRONTEND_URL}})

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(forum_bp, url_prefix='/forum')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(applications_bp, url_prefix='/applications')
    app.register_blueprint(messages_bp, url_prefix='/messages')
    
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)