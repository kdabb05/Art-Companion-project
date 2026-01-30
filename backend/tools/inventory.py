"""Supply Inventory Manager Tool - CRUD operations for art supplies."""

import json
from typing import Optional
from flask import current_app
from backend.models import db, Supply


def inventory_tool(action: str, item: Optional[dict] = None, supply_id: Optional[int] = None, user_id: Optional[int] = None) -> str:
    """
    Manage art supply inventory.
    
    Args:
        action: One of 'list', 'add', 'update', 'delete', 'low_stock', 'get'
        item: Dictionary with supply details for add/update:
              {brand, name, type, quantity, unit, notes}
        supply_id: ID of supply for get/update/delete operations
        user_id: ID of current user (injected by agent)
    
    Returns:
        JSON string with operation result
    """
    try:
        # Base query filtered by user
        base_query = Supply.query
        if user_id:
            base_query = base_query.filter_by(user_id=user_id)
        
        if action == "list":
            supplies = base_query.all()
            return json.dumps({
                "success": True,
                "supplies": [s.to_dict() for s in supplies],
                "count": len(supplies),
            })
        
        elif action == "low_stock":
            # Get supplies with quantity < 0.3
            low_supplies = base_query.filter(Supply.quantity < 0.3).all()
            return json.dumps({
                "success": True,
                "low_stock_supplies": [s.to_dict() for s in low_supplies],
                "count": len(low_supplies),
                "message": f"Found {len(low_supplies)} supplies running low.",
            })
        
        elif action == "get":
            if not supply_id:
                return json.dumps({"success": False, "error": "supply_id required for get"})
            supply = base_query.filter_by(id=supply_id).first()
            if not supply:
                return json.dumps({"success": False, "error": "Supply not found"})
            return json.dumps({"success": True, "supply": supply.to_dict()})
        
        elif action == "add":
            if not item:
                return json.dumps({"success": False, "error": "item details required for add"})
            
            supply = Supply(
                user_id=user_id,
                brand=item.get("brand", "Unknown"),
                name=item.get("name", "Unnamed"),
                type=item.get("type"),
                quantity=item.get("quantity", 1.0),
                unit=item.get("unit"),
                notes=item.get("notes"),
            )
            db.session.add(supply)
            db.session.commit()
            
            return json.dumps({
                "success": True,
                "message": f"Added {supply.brand} {supply.name}",
                "supply": supply.to_dict(),
            })
        
        elif action == "update":
            if not supply_id:
                return json.dumps({"success": False, "error": "supply_id required for update"})
            if not item:
                return json.dumps({"success": False, "error": "item details required for update"})
            
            supply = base_query.filter_by(id=supply_id).first()
            if not supply:
                return json.dumps({"success": False, "error": "Supply not found"})
            
            # Update fields if provided
            for field in ["brand", "name", "type", "quantity", "unit", "notes"]:
                if field in item:
                    setattr(supply, field, item[field])
            
            db.session.commit()
            
            return json.dumps({
                "success": True,
                "message": f"Updated {supply.brand} {supply.name}",
                "supply": supply.to_dict(),
            })
        
        elif action == "delete":
            if not supply_id:
                return json.dumps({"success": False, "error": "supply_id required for delete"})
            
            supply = base_query.filter_by(id=supply_id).first()
            if not supply:
                return json.dumps({"success": False, "error": "Supply not found"})
            
            name = f"{supply.brand} {supply.name}"
            db.session.delete(supply)
            db.session.commit()
            
            return json.dumps({"success": True, "message": f"Deleted {name}"})
        
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown action: {action}",
                "valid_actions": ["list", "add", "update", "delete", "low_stock", "get"],
            })
    
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
