"""Portfolio Storehouse Tool - Store and manage artwork with metadata."""

import json
from typing import Optional
from backend.models import db, Artwork


def portfolio_tool(
    action: str,
    artwork_data: Optional[dict] = None,
    artwork_id: Optional[int] = None,
    filter_by: Optional[dict] = None,
    user_id: Optional[int] = None,
) -> str:
    """
    Manage portfolio of artworks.
    
    Args:
        action: One of 'list', 'add', 'update', 'delete', 'get', 'search'
        artwork_data: Dictionary with artwork details for add/update:
                     {title, image_path, medium, difficulty, date_created, notes, project_id}
        artwork_id: ID of artwork for get/update/delete operations
        filter_by: Dictionary for filtering in search: {medium, difficulty, project_id}
        user_id: ID of current user (injected by agent)
    
    Returns:
        JSON string with operation result
    """
    try:
        # Base query filtered by user
        base_query = Artwork.query
        if user_id:
            base_query = base_query.filter_by(user_id=user_id)
        
        if action == "list":
            artworks = base_query.order_by(Artwork.created_at.desc()).all()
            return json.dumps({
                "success": True,
                "artworks": [a.to_dict() for a in artworks],
                "count": len(artworks),
            })
        
        elif action == "search":
            query = base_query
            
            if filter_by:
                if "medium" in filter_by:
                    query = query.filter(Artwork.medium.ilike(f"%{filter_by['medium']}%"))
                if "difficulty" in filter_by:
                    query = query.filter(Artwork.difficulty == filter_by["difficulty"])
                if "project_id" in filter_by:
                    query = query.filter(Artwork.project_id == filter_by["project_id"])
            
            artworks = query.order_by(Artwork.created_at.desc()).all()
            return json.dumps({
                "success": True,
                "artworks": [a.to_dict() for a in artworks],
                "count": len(artworks),
                "filters_applied": filter_by,
            })
        
        elif action == "get":
            if not artwork_id:
                return json.dumps({"success": False, "error": "artwork_id required for get"})
            artwork = base_query.filter_by(id=artwork_id).first()
            if not artwork:
                return json.dumps({"success": False, "error": "Artwork not found"})
            return json.dumps({"success": True, "artwork": artwork.to_dict()})
        
        elif action == "add":
            if not artwork_data:
                return json.dumps({"success": False, "error": "artwork_data required for add"})
            if "image_path" not in artwork_data:
                return json.dumps({"success": False, "error": "image_path is required"})
            
            artwork = Artwork(
                user_id=user_id,
                title=artwork_data.get("title"),
                image_path=artwork_data["image_path"],
                medium=artwork_data.get("medium"),
                difficulty=artwork_data.get("difficulty"),
                notes=artwork_data.get("notes"),
                project_id=artwork_data.get("project_id"),
            )
            db.session.add(artwork)
            db.session.commit()
            
            return json.dumps({
                "success": True,
                "message": f"Added artwork: {artwork.title or 'Untitled'}",
                "artwork": artwork.to_dict(),
            })
        
        elif action == "update":
            if not artwork_id:
                return json.dumps({"success": False, "error": "artwork_id required for update"})
            if not artwork_data:
                return json.dumps({"success": False, "error": "artwork_data required for update"})
            
            artwork = base_query.filter_by(id=artwork_id).first()
            if not artwork:
                return json.dumps({"success": False, "error": "Artwork not found"})
            
            for field in ["title", "image_path", "medium", "difficulty", "notes", "project_id"]:
                if field in artwork_data:
                    setattr(artwork, field, artwork_data[field])
            
            db.session.commit()
            
            return json.dumps({
                "success": True,
                "message": f"Updated artwork: {artwork.title or 'Untitled'}",
                "artwork": artwork.to_dict(),
            })
        
        elif action == "delete":
            if not artwork_id:
                return json.dumps({"success": False, "error": "artwork_id required for delete"})
            
            artwork = base_query.filter_by(id=artwork_id).first()
            if not artwork:
                return json.dumps({"success": False, "error": "Artwork not found"})
            
            title = artwork.title or "Untitled"
            db.session.delete(artwork)
            db.session.commit()
            
            return json.dumps({"success": True, "message": f"Deleted artwork: {title}"})
        
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown action: {action}",
                "valid_actions": ["list", "add", "update", "delete", "get", "search"],
            })
    
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
