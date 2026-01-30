"""Idea model for saving user ideas and notes."""

from datetime import datetime
from . import db


class Idea(db.Model):
    """A saved idea or note from the user."""
    
    __tablename__ = "ideas"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    
    # Categorization
    category = db.Column(db.String(50))  # "project-idea", "color-palette", "technique", "inspiration", "other"
    tags = db.Column(db.JSON)  # ["watercolor", "landscape", "spring"]
    
    # Optional image attachment
    image_path = db.Column(db.String(500))
    
    # Link to conversation where idea came from
    source_conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"))
    source_message_id = db.Column(db.Integer, db.ForeignKey("messages.id"))
    
    # Status
    is_favorite = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "tags": self.tags or [],
            "image_path": self.image_path,
            "source_conversation_id": self.source_conversation_id,
            "is_favorite": self.is_favorite,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
