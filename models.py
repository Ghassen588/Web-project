from extensions import db, bcrypt
from datetime import datetime, timezone
import enum

# --- Enums ---
class UserRole(enum.Enum):
    STUDENT = "student"
    RECRUITER = "recruiter"

class ApplicationStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REFUSED = "refused"

# --- Association Tables (for Many-to-Many) ---

# Association table for followers
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Association table for saved jobs
saved_jobs = db.Table('saved_jobs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('job_id', db.Integer, db.ForeignKey('job.id'), primary_key=True)
)

# Association table for post likes
post_likes = db.Table('post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

# Association table for comment likes
comment_likes = db.Table('comment_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'), primary_key=True)
)


# --- Main Models ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    
    # Profile information
    bio = db.Column(db.Text, nullable=True)
    study_place = db.Column(db.String(150), nullable=True)
    work_place = db.Column(db.String(150), nullable=True)
    linkedin_link = db.Column(db.String(200), nullable=True)
    github_link = db.Column(db.String(200), nullable=True)
    
    # Relationships
    posts = db.relationship('Post', back_populates='author', lazy='dynamic', cascade="all, delete-orphan")
    comments = db.relationship('Comment', back_populates='author', lazy='dynamic', cascade="all, delete-orphan")
    applications = db.relationship('Application', back_populates='student', lazy='dynamic', cascade="all, delete-orphan")
    jobs_posted = db.relationship('Job', back_populates='recruiter', lazy='dynamic', cascade="all, delete-orphan")
    job_ratings = db.relationship('JobRating', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")
    
    # Many-to-Many Relationships
    jobs_saved = db.relationship('Job', secondary=saved_jobs,
                                 back_populates='saved_by', lazy='dynamic')
    
    liked_posts = db.relationship('Post', secondary=post_likes,
                                  back_populates='liked_by', lazy='dynamic')
    
    liked_comments = db.relationship('Comment', secondary=comment_likes,
                                     back_populates='liked_by', lazy='dynamic')
    
    # Self-referential Many-to-Many for follows
    following = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.firstname} {self.lastname} ({self.email})>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    author = db.relationship('User', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', lazy='dynamic', cascade="all, delete-orphan")
    liked_by = db.relationship('User', secondary=post_likes,
                               back_populates='liked_posts', lazy='dynamic')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    
    author = db.relationship('User', back_populates='comments')
    post = db.relationship('Post', back_populates='comments')
    liked_by = db.relationship('User', secondary=comment_likes,
                               back_populates='liked_comments', lazy='dynamic')

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    salary = db.Column(db.String(100), nullable=True)
    is_remote = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(150), nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    recruiter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    recruiter = db.relationship('User', back_populates='jobs_posted')
    applications = db.relationship('Application', back_populates='job', lazy='dynamic', cascade="all, delete-orphan")
    ratings = db.relationship('JobRating', back_populates='job', lazy='dynamic', cascade="all, delete-orphan")
    saved_by = db.relationship('User', secondary=saved_jobs,
                               back_populates='jobs_saved', lazy='dynamic')

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # The student
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    status = db.Column(db.Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.PENDING)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    
    student = db.relationship('User', back_populates='applications')
    job = db.relationship('Job', back_populates='applications')

class JobRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer, nullable=False) # 0-5
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    
    user = db.relationship('User', back_populates='job_ratings')
    job = db.relationship('Job', back_populates='ratings')
    
    # Ensure a user can only rate a job once
    __table_args__ = (db.UniqueConstraint('user_id', 'job_id', name='_user_job_uc'),)