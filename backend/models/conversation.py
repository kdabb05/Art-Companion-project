"""Conversation and Message models for chat history."""

from datetime import datetime
from . import db


class Conversation(db.Model):
    """A conversation session with the AI agent."""
    
    __tablename__ = "conversations"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    title = db.Column(db.String(200))  # Auto-generated or user-defined
    summary = db.Column(db.Text)  # Brief summary of conversation
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship("Message", backref="conversation", lazy="dynamic", 
                               order_by="Message.created_at", cascade="all, delete-orphan")
    
    def to_dict(self, include_messages=False):
        """Convert to dictionary for JSON serialization."""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title or "Untitled Conversation",
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "message_count": self.messages.count(),
        }
        
        if include_messages:
            data["messages"] = [m.to_dict() for m in self.messages.all()]
        
        return data
    
    def generate_title(self):
        """Generate a title from the first user message."""
        first_message = self.messages.filter_by(role="user").first()
        if first_message:
            # Take first 50 chars of first message
            content = first_message.content[:50]
            self.title = content + "..." if len(first_message.content) > 50 else content


class Message(db.Model):
    """A single message in a conversation."""
    
    __tablename__ = "messages"
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False)
    
    role = db.Column(db.String(20), nullable=False)  # "user", "assistant", "system"
    content = db.Column(db.Text, nullable=False)
    
    # Tool call tracking
    tool_calls = db.Column(db.JSON)  # [{tool, args, result}]
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "tool_calls": self.tool_calls,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
