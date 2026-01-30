"""Project Filesaver Tool - Save and resume project plans."""

import json
from typing import Optional
from backend.models import db, Project


def project_tool(
    action: str,
    project_data: Optional[dict] = None,
    project_id: Optional[int] = None,
    user_id: Optional[int] = None,
) -> str:
    """
    Manage art projects with steps and session notes.
    
    Args:
        action: One of 'list', 'create', 'update', 'delete', 'get', 'add_step', 'update_step', 'add_notes'
        project_data: Dictionary with project details:
                     {title, description, status, steps, supply_list, session_notes}
        project_id: ID of project for operations that target a specific project
        user_id: ID of current user (injected by agent)
    
    Returns:
        JSON string with operation result
    """
    try:
        # Base query filtered by user
        base_query = Project.query
        if user_id:
            base_query = base_query.filter_by(user_id=user_id)
        
        if action == "list":
            projects = base_query.order_by(Project.updated_at.desc()).all()
            return json.dumps({
                "success": True,
                "projects": [p.to_dict() for p in projects],
                "count": len(projects),
            })
        
        elif action == "get":
            if not project_id:
                return json.dumps({"success": False, "error": "project_id required for get"})
            project = base_query.filter_by(id=project_id).first()
            if not project:
                return json.dumps({"success": False, "error": "Project not found"})
            return json.dumps({"success": True, "project": project.to_dict()})
        
        elif action == "create":
            if not project_data:
                return json.dumps({"success": False, "error": "project_data required for create"})
            if "title" not in project_data:
                return json.dumps({"success": False, "error": "title is required"})
            
            project = Project(
                user_id=user_id,
                title=project_data["title"],
                description=project_data.get("description"),
                status=project_data.get("status", "planning"),
                steps=project_data.get("steps", []),
                supply_list=project_data.get("supply_list", []),
                session_notes=project_data.get("session_notes"),
            )
            db.session.add(project)
            db.session.commit()
            
            return json.dumps({
                "success": True,
                "message": f"Created project: {project.title}",
                "project": project.to_dict(),
            })
        
        elif action == "update":
            if not project_id:
                return json.dumps({"success": False, "error": "project_id required for update"})
            if not project_data:
                return json.dumps({"success": False, "error": "project_data required for update"})
            
            project = base_query.filter_by(id=project_id).first()
            if not project:
                return json.dumps({"success": False, "error": "Project not found"})
            
            for field in ["title", "description", "status", "steps", "supply_list", "session_notes"]:
                if field in project_data:
                    setattr(project, field, project_data[field])
            
            db.session.commit()
            
            return json.dumps({
                "success": True,
                "message": f"Updated project: {project.title}",
                "project": project.to_dict(),
            })
        
        elif action == "add_step":
            if not project_id:
                return json.dumps({"success": False, "error": "project_id required for add_step"})
            if not project_data or "instruction" not in project_data:
                return json.dumps({"success": False, "error": "instruction required in project_data"})
            
            project = base_query.filter_by(id=project_id).first()
            if not project:
                return json.dumps({"success": False, "error": "Project not found"})
            
            steps = project.steps or []
            new_step = {
                "step": len(steps) + 1,
                "instruction": project_data["instruction"],
                "completed": False,
            }
            steps.append(new_step)
            project.steps = steps
            db.session.commit()
            
            return json.dumps({
                "success": True,
                "message": f"Added step {new_step['step']} to {project.title}",
                "step": new_step,
                "project": project.to_dict(),
            })
        
        elif action == "update_step":
            if not project_id:
                return json.dumps({"success": False, "error": "project_id required for update_step"})
            if not project_data or "step_number" not in project_data:
                return json.dumps({"success": False, "error": "step_number required in project_data"})
            
            project = base_query.filter_by(id=project_id).first()
            if not project:
                return json.dumps({"success": False, "error": "Project not found"})
            
            steps = project.steps or []
            step_num = project_data["step_number"]
            
            for step in steps:
                if step["step"] == step_num:
                    if "instruction" in project_data:
                        step["instruction"] = project_data["instruction"]
                    if "completed" in project_data:
                        step["completed"] = project_data["completed"]
                    break
            else:
                return json.dumps({"success": False, "error": f"Step {step_num} not found"})
            
            project.steps = steps
            db.session.commit()
            
            return json.dumps({
                "success": True,
                "message": f"Updated step {step_num}",
                "project": project.to_dict(),
            })
        
        elif action == "add_notes":
            if not project_id:
                return json.dumps({"success": False, "error": "project_id required for add_notes"})
            if not project_data or "notes" not in project_data:
                return json.dumps({"success": False, "error": "notes required in project_data"})
            
            project = base_query.filter_by(id=project_id).first()
            if not project:
                return json.dumps({"success": False, "error": "Project not found"})
            
            # Append to existing notes
            existing = project.session_notes or ""
            separator = "\n\n---\n\n" if existing else ""
            project.session_notes = existing + separator + project_data["notes"]
            db.session.commit()
            
            return json.dumps({
                "success": True,
                "message": "Added session notes",
                "project": project.to_dict(),
            })
        
        elif action == "delete":
            if not project_id:
                return json.dumps({"success": False, "error": "project_id required for delete"})
            
            project = base_query.filter_by(id=project_id).first()
            if not project:
                return json.dumps({"success": False, "error": "Project not found"})
            
            title = project.title
            db.session.delete(project)
            db.session.commit()
            
            return json.dumps({"success": True, "message": f"Deleted project: {title}"})
        
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown action: {action}",
                "valid_actions": ["list", "create", "update", "delete", "get", "add_step", "update_step", "add_notes"],
            })
    
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
