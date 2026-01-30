"""Authentication routes for user registration, login, and logout."""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from backend.models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate required fields
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower() if data.get("email") else None
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400
    
    if email and User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400
    
    # Create new user
    user = User(
        username=username,
        email=email,
        display_name=data.get("display_name", username),
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    # Log the user in
    login_user(user, remember=True)
    
    return jsonify({
        "message": "Registration successful",
        "user": user.to_dict(include_preferences=True),
        "needs_onboarding": True,
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Log in an existing user."""
    data = request.get_json()
    
    # Accept username or email
    login_id = data.get("username") or data.get("email", "")
    password = data.get("password", "")
    remember = data.get("remember", True)
    
    if not login_id or not password:
        return jsonify({"error": "Username/email and password are required"}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == login_id) | (User.email == login_id.lower())
    ).first()
    
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username/email or password"}), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Log the user in
    login_user(user, remember=remember)
    
    return jsonify({
        "message": "Login successful",
        "user": user.to_dict(include_preferences=True),
        "needs_onboarding": not user.onboarding_completed,
    })


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    return jsonify({"message": "Logged out successfully"})


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """Get the current logged-in user."""
    if current_user.is_authenticated:
        return jsonify({
            "authenticated": True,
            "user": current_user.to_dict(include_preferences=True),
            "needs_onboarding": not current_user.onboarding_completed,
        })
    return jsonify({"authenticated": False})


@auth_bp.route("/onboarding", methods=["POST"])
@login_required
def complete_onboarding():
    """Save user preferences from onboarding."""
    data = request.get_json()
    
    # Update preferences
    current_user.favorite_mediums = data.get("favorite_mediums", [])
    current_user.favorite_styles = data.get("favorite_styles", [])
    current_user.skill_level = data.get("skill_level")
    current_user.session_length = data.get("session_length")
    current_user.budget_range = data.get("budget_range")
    current_user.goals = data.get("goals")
    current_user.pinterest_username = data.get("pinterest_username")
    
    # Mark onboarding as complete
    current_user.onboarding_completed = True
    
    db.session.commit()
    
    return jsonify({
        "message": "Preferences saved",
        "user": current_user.to_dict(include_preferences=True),
    })


@auth_bp.route("/preferences", methods=["PUT"])
@login_required
def update_preferences():
    """Update user preferences."""
    data = request.get_json()
    
    # Update only provided fields
    if "display_name" in data:
        current_user.display_name = data["display_name"]
    if "favorite_mediums" in data:
        current_user.favorite_mediums = data["favorite_mediums"]
    if "favorite_styles" in data:
        current_user.favorite_styles = data["favorite_styles"]
    if "skill_level" in data:
        current_user.skill_level = data["skill_level"]
    if "session_length" in data:
        current_user.session_length = data["session_length"]
    if "budget_range" in data:
        current_user.budget_range = data["budget_range"]
    if "goals" in data:
        current_user.goals = data["goals"]
    if "pinterest_username" in data:
        current_user.pinterest_username = data["pinterest_username"]
    
    db.session.commit()
    
    return jsonify({
        "message": "Preferences updated",
        "user": current_user.to_dict(include_preferences=True),
    })
