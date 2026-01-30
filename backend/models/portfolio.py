"""Portfolio model for artwork storage."""

from datetime import datetime, date
from . import db


class Artwork(db.Model):
    """Artwork in the portfolio with metadata and copyright protection."""
    
    __tablename__ = "artworks"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    title = db.Column(db.String(200))
    image_path = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(255))  # Original uploaded filename
    file_type = db.Column(db.String(10))  # jpeg, png, pdf
    medium = db.Column(db.String(100))  # watercolor, oil, digital, etc.
    difficulty = db.Column(db.Integer)  # 1-5 scale
    date_created = db.Column(db.Date, default=date.today)
    notes = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Copyright protection fields
    is_copyrighted = db.Column(db.Boolean, default=True)
    copyright_notice = db.Column(db.String(500))
    allow_download = db.Column(db.Boolean, default=False)
    allow_sharing = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "image_path": self.image_path,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "medium": self.medium,
            "difficulty": self.difficulty,
            "date_created": self.date_created.isoformat() if self.date_created else None,
            "notes": self.notes,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_copyrighted": self.is_copyrighted,
            "copyright_notice": self.copyright_notice,
            "allow_download": self.allow_download,
            "allow_sharing": self.allow_sharing,
        }
