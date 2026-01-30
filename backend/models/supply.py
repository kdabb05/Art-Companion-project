"""Supply inventory model."""

from datetime import datetime
from . import db


class Supply(db.Model):
    """Art supply inventory item."""
    
    __tablename__ = "supplies"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # nullable for migration
    brand = db.Column(db.String(100), nullable=True)  # Optional
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))  # paint, brush, canvas, yarn, etc.
    colors = db.Column(db.JSON, default=list)  # List of {name, hex} objects for multiple colors
    quantity = db.Column(db.Integer, default=1)  # Whole number count
    unit = db.Column(db.String(20))  # tube, skein, sheet, piece
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "brand": self.brand,
            "name": self.name,
            "type": self.type,
            "colors": self.colors or [],
            "quantity": self.quantity,
            "unit": self.unit,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @property
    def stock_status(self):
        """Return stock status: 'plenty', 'low', or 'empty'."""
        if self.quantity <= 0:
            return "empty"
        elif self.quantity <= 2:
            return "low"
        return "plenty"
