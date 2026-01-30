"""Project model for art project planning."""

from datetime import datetime
from . import db


class Project(db.Model):
    """Art project with steps and session notes."""
    
    __tablename__ = "projects"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # nullable for migration
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default="planning")  # planning, in_progress, completed
    description = db.Column(db.Text)
    steps = db.Column(db.JSON)  # [{step: 1, instruction: "...", completed: false}]
    supply_list = db.Column(db.JSON)  # [supply_id, ...]
    session_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationship to artworks
    artworks = db.relationship("Artwork", backref="project", lazy=True)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "description": self.description,
            "steps": self.steps or [],
            "supply_list": self.supply_list or [],
            "session_notes": self.session_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
