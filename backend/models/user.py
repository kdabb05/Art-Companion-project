"""User model with preferences and authentication."""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    """User account with preferences."""
    
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)  # Optional
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profile
    display_name = db.Column(db.String(100))
    avatar_path = db.Column(db.String(500))
    
    # Preferences (collected during onboarding)
    favorite_mediums = db.Column(db.JSON)  # ["watercolor", "oil", "digital"]
    favorite_styles = db.Column(db.JSON)   # ["impressionist", "abstract", "realism"]
    skill_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    session_length = db.Column(db.String(50))  # "1-hour weeknight", "full day weekend"
    budget_range = db.Column(db.String(50))  # "tight", "moderate", "flexible"
    goals = db.Column(db.Text)  # What they want to achieve
    
    # Pinterest integration
    pinterest_username = db.Column(db.String(100))
    pinterest_connected = db.Column(db.Boolean, default=False)
    
    # Onboarding status
    onboarding_completed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    supplies = db.relationship("Supply", backref="owner", lazy="dynamic")
    projects = db.relationship("Project", backref="owner", lazy="dynamic")
    artworks = db.relationship("Artwork", backref="owner", lazy="dynamic")
    conversations = db.relationship("Conversation", backref="owner", lazy="dynamic")
    ideas = db.relationship("Idea", backref="owner", lazy="dynamic")
    
    def set_password(self, password):
        """Hash and set the password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_preferences=False):
        """Convert to dictionary for JSON serialization."""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "display_name": self.display_name or self.username,
            "avatar_path": self.avatar_path,
            "onboarding_completed": self.onboarding_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_preferences:
            data.update({
                "favorite_mediums": self.favorite_mediums or [],
                "favorite_styles": self.favorite_styles or [],
                "skill_level": self.skill_level,
                "session_length": self.session_length,
                "budget_range": self.budget_range,
                "goals": self.goals,
                "pinterest_username": self.pinterest_username,
                "pinterest_connected": self.pinterest_connected,
            })
        
        return data
