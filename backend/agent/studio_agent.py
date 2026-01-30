"""Studio Companion Agent - LLM agent with art studio tools via OpenRouter."""

import json
import os
from typing import Optional
import requests
from backend.config import Config

# Agent singleton
_agent_instance: Optional["StudioAgent"] = None

SYSTEM_PROMPT = """You are the Art Studio Companion, a friendly assistant for artists.

Help users with:
- Art project planning and ideas
- Supply inventory management  
- Creative inspiration
- Step-by-step instructions

Be concise but helpful. Use tools when managing supplies, projects, or getting inspiration.

IMPORTANT Pinterest guidelines:
- When a user asks for Pinterest inspiration, use the inspiration_tool with a descriptive theme including their specified colors and style
- Always include the pin_url links in your response as clickable markdown links like [Title](url)
- Show the REAL titles returned by the tool - never make up fake descriptions
- If the tool returns a search link, provide it so the user can browse Pinterest directly
"""

# Tool definitions for the LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "inspiration_tool",
            "description": "Search Pinterest for inspiration images matching a theme, colors, or style. Returns real Pinterest pins with clickable links. Use this when the user asks for visual inspiration or Pinterest ideas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "theme": {
                        "type": "string",
                        "description": "The inspiration theme including colors and style. Be specific, e.g., 'purple blue green landscape watercolor', 'cozy autumn crochet blanket', 'abstract ocean waves painting'"
                    },
                    "style": {
                        "type": "string",
                        "description": "Optional additional style preference (e.g., 'loose', 'detailed', 'cozy', 'modern')"
                    },
                    "pinterest_board": {
                        "type": "string",
                        "description": "Optional: user's Pinterest board URL to browse their saved pins instead of searching"
                    }
                },
                "required": ["theme"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "inventory_tool",
            "description": "Manage art supply inventory. Actions: 'list' (all supplies), 'add' (new supply), 'update' (existing supply), 'low_stock' (supplies running low)",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "add", "update", "delete", "low_stock", "get"],
                        "description": "The action to perform"
                    },
                    "item": {
                        "type": "object",
                        "description": "Supply details for add/update: {brand, name, type, quantity, unit, notes}",
                        "properties": {
                            "brand": {"type": "string"},
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "quantity": {"type": "number"},
                            "unit": {"type": "string"},
                            "notes": {"type": "string"}
                        }
                    },
                    "supply_id": {
                        "type": "integer",
                        "description": "ID of supply for get/update/delete"
                    }
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "portfolio_tool",
            "description": "Manage portfolio of artworks. Actions: 'list', 'add', 'get', 'search', 'update', 'delete'",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "add", "update", "delete", "get", "search"],
                        "description": "The action to perform"
                    },
                    "artwork_data": {
                        "type": "object",
                        "description": "Artwork details: {title, image_path, medium, difficulty, notes, project_id}"
                    },
                    "artwork_id": {"type": "integer"},
                    "filter_by": {
                        "type": "object",
                        "description": "Filters for search: {medium, difficulty, project_id}"
                    }
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "project_tool",
            "description": "Manage art projects. Actions: 'list', 'create', 'get', 'update', 'add_step', 'update_step', 'add_notes', 'delete'",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "create", "update", "delete", "get", "add_step", "update_step", "add_notes"],
                        "description": "The action to perform"
                    },
                    "project_data": {
                        "type": "object",
                        "description": "Project details: {title, description, status, steps, supply_list, session_notes}"
                    },
                    "project_id": {"type": "integer"}
                },
                "required": ["action"]
            }
        }
    }
]


class StudioAgent:
    """Agent wrapper using OpenRouter API with tool calling."""
    
    def __init__(self):
        """Initialize the agent."""
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.LETTA_MODEL
        self.endpoint = Config.LETTA_LLM_ENDPOINT
        self.conversation_history = []
        self._tools_imported = False
        self.user_context = None
        self.current_user_id = None
        
    def set_user_context(self, user):
        """Set the current user's context and preferences."""
        if user is None:
            self.user_context = None
            self.current_user_id = None
            return
            
        self.current_user_id = user.id
        
        # Build user context string from preferences
        context_parts = [f"Current user: {user.username}"]
        
        if user.favorite_mediums:
            context_parts.append(f"Favorite mediums: {', '.join(user.favorite_mediums)}")
        if user.favorite_styles:
            context_parts.append(f"Preferred styles: {', '.join(user.favorite_styles)}")
        if user.skill_level:
            context_parts.append(f"Skill level: {user.skill_level}")
        if user.session_length:
            context_parts.append(f"Typical session length: {user.session_length}")
        if user.budget_range:
            context_parts.append(f"Budget range: {user.budget_range}")
        if user.goals:
            context_parts.append(f"Goals: {user.goals}")
        if user.pinterest_username:
            context_parts.append(f"Pinterest: @{user.pinterest_username}")
            
        self.user_context = "\n".join(context_parts)
    
    def set_guest_context(self, preferences: dict):
        """Set context from guest preferences (not persisted)."""
        self.current_user_id = None
        
        if not preferences:
            self.user_context = "Current user: Guest (no preferences set)"
            return
        
        context_parts = ["Current user: Guest"]
        
        if preferences.get("favorite_mediums"):
            mediums = preferences["favorite_mediums"]
            if isinstance(mediums, list):
                context_parts.append(f"Favorite mediums: {', '.join(mediums)}")
        if preferences.get("favorite_styles"):
            styles = preferences["favorite_styles"]
            if isinstance(styles, list):
                context_parts.append(f"Preferred styles: {', '.join(styles)}")
        if preferences.get("skill_level"):
            context_parts.append(f"Skill level: {preferences['skill_level']}")
        if preferences.get("session_length"):
            context_parts.append(f"Typical session length: {preferences['session_length']}")
        if preferences.get("budget_range"):
            context_parts.append(f"Budget range: {preferences['budget_range']}")
        if preferences.get("goals"):
            context_parts.append(f"Goals: {preferences['goals']}")
            
        self.user_context = "\n".join(context_parts)
        
    def _import_tools(self):
        """Import tool functions lazily to avoid circular imports."""
        if self._tools_imported:
            return
        from backend.tools import inspiration_tool, inventory_tool, portfolio_tool, project_tool
        self._tool_functions = {
            "inspiration_tool": inspiration_tool,
            "inventory_tool": inventory_tool,
            "portfolio_tool": portfolio_tool,
            "project_tool": project_tool,
        }
        self._tools_imported = True
    
    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool and return the result."""
        self._import_tools()
        
        if tool_name not in self._tool_functions:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})
        
        try:
            tool_fn = self._tool_functions[tool_name]
            # Inject user_id into all tool calls for proper scoping
            if self.current_user_id:
                arguments["user_id"] = self.current_user_id
            result = tool_fn(**arguments)
            return result
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def send_message(self, message: str) -> dict:
        """
        Send a message to the agent and get a response.
        
        Args:
            message: User's message
            
        Returns:
            Dictionary with agent response and any tool calls made
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenRouter API key not configured",
                "response": "I'm not configured yet. Please add your OPENROUTER_API_KEY to the .env file.",
                "tool_calls": [],
            }
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        tool_calls_made = []
        
        try:
            # Make initial API call
            response = self._call_openrouter(include_tools=True)
            
            # Handle tool calls if present
            while response.get("tool_calls"):
                for tool_call in response["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    arguments = json.loads(tool_call["function"]["arguments"])
                    
                    # Execute the tool
                    tool_result = self._execute_tool(tool_name, arguments)
                    
                    tool_calls_made.append({
                        "tool": tool_name,
                        "args": arguments,
                        "result": tool_result,
                    })
                    
                    # Add tool call and result to history
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": tool_result
                    })
                
                # Get next response after tool execution
                response = self._call_openrouter(include_tools=True)
            
            # Extract final text response
            assistant_message = response.get("content", "")
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return {
                "success": True,
                "response": assistant_message,
                "tool_calls": tool_calls_made,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"I encountered an error: {str(e)}. Please try again.",
                "tool_calls": tool_calls_made,
            }
    
    def _call_openrouter(self, include_tools: bool = True) -> dict:
        """Make a call to OpenRouter API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "Art Studio Companion",
        }
        
        # Build system prompt with user context
        system_content = SYSTEM_PROMPT
        if self.user_context:
            system_content += f"\n\nUser: {self.user_context}"
        
        # Limit conversation history to last 10 messages to save tokens
        recent_history = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history
        
        messages = [{"role": "system", "content": system_content}] + recent_history
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500,  # Reduced for cost savings
        }
        
        if include_tools:
            payload["tools"] = TOOLS
            payload["tool_choice"] = "auto"
        
        response = requests.post(
            f"{self.endpoint}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        
        if response.status_code != 200:
            error_detail = response.json().get("error", {}).get("message", response.text)
            raise Exception(f"OpenRouter API error: {error_detail}")
        
        data = response.json()
        choice = data["choices"][0]["message"]
        
        return {
            "content": choice.get("content"),
            "tool_calls": choice.get("tool_calls"),
        }
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


def get_agent() -> StudioAgent:
    """Get or create the singleton agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = StudioAgent()
    return _agent_instance
