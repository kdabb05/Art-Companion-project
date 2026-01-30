"""Ideas routes for managing saved ideas and notes."""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models import db, Idea

ideas_bp = Blueprint("ideas", __name__, url_prefix="/api/ideas")


@ideas_bp.route("", methods=["GET"])
@login_required
def list_ideas():
    """List all ideas for the current user."""
    # Optional filters
    category = request.args.get("category")
    is_favorite = request.args.get("favorite")
    is_archived = request.args.get("archived", "false").lower() == "true"
    
    query = Idea.query.filter_by(user_id=current_user.id, is_archived=is_archived)
    
    if category:
        query = query.filter_by(category=category)
    if is_favorite:
        query = query.filter_by(is_favorite=True)
    
    ideas = query.order_by(Idea.updated_at.desc()).all()
    
    return jsonify({
        "ideas": [i.to_dict() for i in ideas],
        "count": len(ideas),
    })


@ideas_bp.route("", methods=["POST"])
@login_required
def create_idea():
    """Create a new idea."""
    data = request.get_json()
    
    if not data.get("title"):
        return jsonify({"error": "Title is required"}), 400
    
    idea = Idea(
        user_id=current_user.id,
        title=data["title"],
        content=data.get("content"),
        category=data.get("category", "other"),
        tags=data.get("tags", []),
        image_path=data.get("image_path"),
        source_conversation_id=data.get("source_conversation_id"),
        source_message_id=data.get("source_message_id"),
    )
    db.session.add(idea)
    db.session.commit()
    
    return jsonify({
        "idea": idea.to_dict(),
    }), 201


@ideas_bp.route("/<int:idea_id>", methods=["GET"])
@login_required
def get_idea(idea_id):
    """Get a single idea."""
    idea = Idea.query.filter_by(
        id=idea_id,
        user_id=current_user.id
    ).first_or_404()
    
    return jsonify({
        "idea": idea.to_dict(),
    })


@ideas_bp.route("/<int:idea_id>", methods=["PUT"])
@login_required
def update_idea(idea_id):
    """Update an idea."""
    idea = Idea.query.filter_by(
        id=idea_id,
        user_id=current_user.id
    ).first_or_404()
    
    data = request.get_json()
    
    for field in ["title", "content", "category", "tags", "image_path", "is_favorite", "is_archived"]:
        if field in data:
            setattr(idea, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        "idea": idea.to_dict(),
    })


@ideas_bp.route("/<int:idea_id>", methods=["DELETE"])
@login_required
def delete_idea(idea_id):
    """Delete an idea."""
    idea = Idea.query.filter_by(
        id=idea_id,
        user_id=current_user.id
    ).first_or_404()
    
    db.session.delete(idea)
    db.session.commit()
    
    return jsonify({"message": "Idea deleted"})


@ideas_bp.route("/<int:idea_id>/favorite", methods=["POST"])
@login_required
def toggle_favorite(idea_id):
    """Toggle favorite status of an idea."""
    idea = Idea.query.filter_by(
        id=idea_id,
        user_id=current_user.id
    ).first_or_404()
    
    idea.is_favorite = not idea.is_favorite
    db.session.commit()
    
    return jsonify({
        "idea": idea.to_dict(),
        "is_favorite": idea.is_favorite,
    })


@ideas_bp.route("/<int:idea_id>/archive", methods=["POST"])
@login_required
def toggle_archive(idea_id):
    """Toggle archive status of an idea."""
    idea = Idea.query.filter_by(
        id=idea_id,
        user_id=current_user.id
    ).first_or_404()
    
    idea.is_archived = not idea.is_archived
    db.session.commit()
    
    return jsonify({
        "idea": idea.to_dict(),
        "is_archived": idea.is_archived,
    })


@ideas_bp.route("/categories", methods=["GET"])
@login_required
def get_categories():
    """Get list of idea categories."""
    return jsonify({
        "categories": [
            {"id": "project-idea", "name": "Project Ideas", "icon": "💡"},
            {"id": "color-palette", "name": "Color Palettes", "icon": "🎨"},
            {"id": "technique", "name": "Techniques", "icon": "🖌️"},
            {"id": "inspiration", "name": "Inspiration", "icon": "✨"},
            {"id": "reference", "name": "References", "icon": "📷"},
            {"id": "other", "name": "Other", "icon": "📝"},
        ]
    })
