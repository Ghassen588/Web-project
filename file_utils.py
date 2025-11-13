import os
import secrets
from werkzeug.utils import secure_filename
from pathlib import Path

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
PROFILE_PICS_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'profile_pics')

# Create folders if they don't exist
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(PROFILE_PICS_FOLDER).mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_image_file(filename):
    """Check if file is an allowed image"""
    allowed_image_ext = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_image_ext


def save_post_file(file):
    """Save uploaded file from post and return relative path"""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        raise ValueError(f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
    
    if file.content_length and file.content_length > MAX_FILE_SIZE:
        raise ValueError(f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB")
    
    # Generate unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{secrets.token_hex(8)}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    # Save file
    file.save(filepath)
    
    # Return relative path for database storage
    return f"uploads/{unique_filename}"


def save_profile_picture(file, user_id):
    """Save profile picture and return relative path"""
    if not file or file.filename == '':
        return None
    
    if not allowed_image_file(file.filename):
        raise ValueError("Profile picture must be an image (PNG, JPG, JPEG, GIF)")
    
    if file.content_length and file.content_length > 5 * 1024 * 1024:  # 5MB for profile pics
        raise ValueError("File too large. Maximum size: 5MB")
    
    # Generate unique filename with user_id
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"profile_{user_id}_{secrets.token_hex(4)}.{ext}"
    filepath = os.path.join(PROFILE_PICS_FOLDER, unique_filename)
    
    # Save file
    file.save(filepath)
    
    # Return relative path for database storage
    return f"profile_pics/{unique_filename}"


def delete_file(file_path):
    """Delete a file from the system"""
    if not file_path:
        return
    
    try:
        full_path = os.path.join(os.path.dirname(__file__), 'static', file_path.lstrip('/static/'))
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")


def is_image_file(file_path):
    """Check if file is an image based on extension"""
    if not file_path:
        return False
    ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''
    return ext in {'png', 'jpg', 'jpeg', 'gif'}


def is_pdf_file(file_path):
    """Check if file is a PDF based on extension"""
    if not file_path:
        return False
    return file_path.lower().endswith('.pdf')
