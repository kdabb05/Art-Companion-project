"""Conversation routes for chat history management."""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models import db, Conversation, Message

conversations_bp = Blueprint("conversations", __name__, url_prefix="/api/conversations")


@conversations_bp.route("", methods=["GET"])
@login_required
def list_conversations():
    """List all conversations for the current user."""
    conversations = Conversation.query.filter_by(user_id=current_user.id)\
        .order_by(Conversation.updated_at.desc()).all()
    
    return jsonify({
        "conversations": [c.to_dict() for c in conversations],
        "count": len(conversations),
    })


@conversations_bp.route("", methods=["POST"])
@login_required
def create_conversation():
    """Create a new conversation."""
    data = request.get_json() or {}
    
    conversation = Conversation(
        user_id=current_user.id,
        title=data.get("title", "New Conversation"),
    )
    db.session.add(conversation)
    db.session.commit()
    
    return jsonify({
        "conversation": conversation.to_dict(),
    }), 201


@conversations_bp.route("/<int:conversation_id>", methods=["GET"])
@login_required
def get_conversation(conversation_id):
    """Get a conversation with all messages."""
    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=current_user.id
    ).first_or_404()
    
    return jsonify({
        "conversation": conversation.to_dict(include_messages=True),
    })


@conversations_bp.route("/<int:conversation_id>", methods=["PUT"])
@login_required
def update_conversation(conversation_id):
    """Update a conversation (e.g., rename)."""
    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=current_user.id
    ).first_or_404()
    
    data = request.get_json()
    
    if "title" in data:
        conversation.title = data["title"]
    if "summary" in data:
        conversation.summary = data["summary"]
    
    db.session.commit()
    
    return jsonify({
        "conversation": conversation.to_dict(),
    })


@conversations_bp.route("/<int:conversation_id>", methods=["DELETE"])
@login_required
def delete_conversation(conversation_id):
    """Delete a conversation and all its messages."""
    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=current_user.id
    ).first_or_404()
    
    db.session.delete(conversation)
    db.session.commit()
    
    return jsonify({"message": "Conversation deleted"})


@conversations_bp.route("/<int:conversation_id>/messages", methods=["GET"])
@login_required
def get_messages(conversation_id):
    """Get all messages in a conversation."""
    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=current_user.id
    ).first_or_404()
    
    messages = conversation.messages.all()
    
    return jsonify({
        "messages": [m.to_dict() for m in messages],
        "count": len(messages),
    })
