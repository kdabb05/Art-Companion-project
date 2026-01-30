"""SQLAlchemy models for Art Studio Companion."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .supply import Supply
from .project import Project
from .portfolio import Artwork
from .conversation import Conversation, Message
from .idea import Idea

__all__ = ["db", "User", "Supply", "Project", "Artwork", "Conversation", "Message", "Idea"]
