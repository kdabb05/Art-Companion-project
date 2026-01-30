"""Pinterest Inspiration Tool - Fetch themed images and color palettes from Pinterest."""

import json
import random
import re
import requests
from typing import Optional, List, Dict


# Fallback inspiration data when Pinterest fetch fails
FALLBACK_INSPIRATIONS = {
    "botanical": [
        {"title": "Watercolor Botanicals", "colors": ["#2d5a27", "#8bc34a", "#f5f5dc"], "style": "loose"},
        {"title": "Pressed Flower Study", "colors": ["#e8d5b7", "#7b5544", "#4a7c59"], "style": "detailed"},
    ],
    "cityscape": [
        {"title": "Moody Urban Night", "colors": ["#1a1a2e", "#16213e", "#e94560"], "style": "atmospheric"},
        {"title": "Golden Hour Skyline", "colors": ["#ff9a3c", "#ff6b6b", "#2c3e50"], "style": "warm"},
    ],
    "portrait": [
        {"title": "Expressive Portrait", "colors": ["#f5cba7", "#d35400", "#2c3e50"], "style": "bold"},
        {"title": "Soft Light Study", "colors": ["#ffeaa7", "#fab1a0", "#dfe6e9"], "style": "soft"},
    ],
    "abstract": [
        {"title": "Color Field Exploration", "colors": ["#6c5ce7", "#a29bfe", "#fd79a8"], "style": "minimalist"},
        {"title": "Gestural Energy", "colors": ["#00b894", "#fdcb6e", "#e17055"], "style": "dynamic"},
    ],
    "crochet": [
        {"title": "Cozy Textures", "colors": ["#d4a574", "#8b7355", "#f5f5dc"], "style": "warm"},
        {"title": "Modern Crochet", "colors": ["#e8d5b7", "#c9b896", "#a69076"], "style": "neutral"},
    ],
    "knitting": [
        {"title": "Cable Patterns", "colors": ["#5d4e37", "#8b7355", "#c4b7a6"], "style": "classic"},
        {"title": "Colorwork Inspiration", "colors": ["#c44536", "#2d6a4f", "#f4a261"], "style": "bold"},
    ],
}


def fetch_pinterest_board(board_url: str, limit: int = 6) -> List[Dict]:
    """
    Fetch pins from a public Pinterest board.
    
    Args:
        board_url: Full Pinterest board URL or username/boardname format
        limit: Maximum number of pins to fetch
        
    Returns:
        List of pin data dictionaries with real titles
    """
    # Normalize URL format
    if not board_url.startswith("http"):
        # Handle username/boardname format
        board_url = f"https://www.pinterest.com/{board_url}/"
    
    # Clean up URL
    board_url = board_url.rstrip("/") + "/"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        response = requests.get(board_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html = response.text
        pins = []
        
        # Extract pin IDs from the HTML
        pin_id_pattern = r'/pin/(\d+)/'
        all_pin_ids = list(set(re.findall(pin_id_pattern, html)))
        
        # Shuffle to get different pins each time
        random.shuffle(all_pin_ids)
        pin_ids = all_pin_ids[:limit]
        
        # Fetch the actual title for each pin
        for pin_id in pin_ids:
            pin_url = f"https://www.pinterest.com/pin/{pin_id}/"
            pin_data = {
                "pin_url": pin_url,
                "title": "",
            }
            
            # Try to fetch the pin's actual title
            try:
                pin_response = requests.get(pin_url, headers=headers, timeout=5)
                if pin_response.status_code == 200:
                    # Extract title from <title> tag
                    title_match = re.search(r'<title>([^<]+)</title>', pin_response.text)
                    if title_match:
                        raw_title = title_match.group(1)
                        # Clean up Pinterest title format (usually "Description | Category, tags")
                        # Take the first part before the pipe
                        if " | " in raw_title:
                            pin_data["title"] = raw_title.split(" | ")[0].strip()
                        else:
                            pin_data["title"] = raw_title.strip()
            except requests.RequestException:
                # If we can't fetch the title, just use the URL
                pass
            
            if not pin_data["title"]:
                pin_data["title"] = f"Pin {pin_id}"
            
            pins.append(pin_data)
        
        return pins
        
    except requests.RequestException as e:
        print(f"Pinterest fetch error: {e}")
        return []


def search_pinterest_pins(query: str, limit: int = 6) -> List[Dict]:
    """
    Search Pinterest for pins matching a query.
    
    Note: Pinterest search results are JavaScript-rendered, so this function
    may have limited success. Falls back to curated inspiration links.
    
    Args:
        query: Search terms (e.g., "purple blue green landscape watercolor")
        limit: Maximum number of pins to fetch
        
    Returns:
        List of pin data dictionaries with titles and URLs
    """
    # Curated Pinterest searches that reliably have good art content
    # Map common themes to known good search terms
    curated_searches = {
        "landscape": "landscape painting inspiration",
        "watercolor": "watercolor art tutorial",
        "purple": "purple aesthetic art",
        "blue": "blue painting art",
        "green": "green nature painting",
        "ocean": "ocean waves painting",
        "sunset": "sunset landscape painting",
        "flower": "flower painting botanical",
        "abstract": "abstract art colorful",
        "portrait": "portrait painting art",
        "crochet": "crochet pattern ideas",
        "knitting": "knitting pattern inspiration",
    }
    
    # Try to find a matching curated search
    query_lower = query.lower()
    search_term = query  # Default to user's query
    for keyword, curated in curated_searches.items():
        if keyword in query_lower:
            search_term = curated
            break
    
    # URL encode the query
    import urllib.parse
    encoded_query = urllib.parse.quote(search_term)
    search_url = f"https://www.pinterest.com/search/pins/?q={encoded_query}"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html = response.text
        pins = []
        
        # Extract pin IDs from the search results
        pin_id_pattern = r'/pin/(\d+)/'
        all_pin_ids = list(set(re.findall(pin_id_pattern, html)))
        
        if not all_pin_ids:
            # Pinterest search didn't return pins in HTML (JS-rendered)
            # Return a link to the search page instead
            return [{
                "title": f"Pinterest Search: {query}",
                "pin_url": search_url,
                "is_search_link": True,
            }]
        
        # Shuffle for variety
        random.shuffle(all_pin_ids)
        pin_ids = all_pin_ids[:limit * 2]
        
        # Fetch title for each pin and validate
        for pin_id in pin_ids:
            if len(pins) >= limit:
                break
                
            pin_url = f"https://www.pinterest.com/pin/{pin_id}/"
            
            try:
                pin_response = requests.get(pin_url, headers=headers, timeout=5)
                if pin_response.status_code == 200:
                    pin_html = pin_response.text
                    
                    # Check if it's a valid pin
                    if "Sorry" in pin_html and "doesn't exist" in pin_html:
                        continue
                    
                    # Extract title
                    title = ""
                    title_match = re.search(r'<title>([^<]+)</title>', pin_html)
                    if title_match:
                        raw_title = title_match.group(1)
                        if " | " in raw_title:
                            title = raw_title.split(" | ")[0].strip()
                        else:
                            title = raw_title.strip()
                    
                    if not title or title == "Pinterest" or len(title) < 5:
                        continue
                    
                    pins.append({
                        "pin_url": pin_url,
                        "title": title,
                    })
            except requests.RequestException:
                continue
        
        # If we couldn't get individual pins, return search link
        if not pins:
            return [{
                "title": f"Browse Pinterest for: {query}",
                "pin_url": search_url,
                "is_search_link": True,
            }]
        
        return pins
        
    except requests.RequestException as e:
        print(f"Pinterest search error: {e}")
        return []


def generate_color_palette_suggestion(theme: str) -> List[str]:
    """Generate a suggested color palette based on theme keywords."""
    theme_lower = theme.lower()
    
    # Color associations
    palettes = {
        "warm": ["#e74c3c", "#f39c12", "#e67e22", "#d35400"],
        "cool": ["#3498db", "#2980b9", "#1abc9c", "#16a085"],
        "earth": ["#8b4513", "#a0522d", "#d2691e", "#deb887"],
        "pastel": ["#ffb3ba", "#bae1ff", "#baffc9", "#ffffba"],
        "moody": ["#2c3e50", "#34495e", "#7f8c8d", "#95a5a6"],
        "vibrant": ["#e74c3c", "#9b59b6", "#3498db", "#2ecc71"],
        "nature": ["#27ae60", "#2ecc71", "#f1c40f", "#e67e22"],
        "ocean": ["#0077be", "#00a8cc", "#a3d9ff", "#f0f8ff"],
        "sunset": ["#ff6b6b", "#ffa07a", "#ffd93d", "#6a0572"],
        "forest": ["#228b22", "#2d5a27", "#556b2f", "#8fbc8f"],
        "autumn": ["#d2691e", "#ff8c00", "#8b4513", "#cd853f"],
        "spring": ["#ff69b4", "#98fb98", "#ffb6c1", "#90ee90"],
        "winter": ["#4169e1", "#b0c4de", "#f0f8ff", "#708090"],
        "cozy": ["#d2691e", "#8b4513", "#f5f5dc", "#deb887"],
        "yarn": ["#d4a574", "#8b7355", "#a0522d", "#f5f5dc"],
    }
    
    # Find matching palette
    for keyword, colors in palettes.items():
        if keyword in theme_lower:
            return colors
    
    # Default varied palette
    return ["#3498db", "#e74c3c", "#f39c12", "#2ecc71", "#9b59b6"]


def inspiration_tool(
    theme: str, 
    style: Optional[str] = None, 
    pinterest_board: Optional[str] = None,
    use_pinterest_search: Optional[bool] = True,
    user_id: Optional[int] = None
) -> str:
    """
    Fetch inspiration images and color palettes based on a theme.
    
    Can search Pinterest for relevant pins or fetch from a specific board.
    
    Args:
        theme: The inspiration theme (e.g., "purple blue green landscape watercolor")
        style: Optional style preference (e.g., "loose", "detailed", "bold")
        pinterest_board: Optional Pinterest board URL to browse user's saved pins
        use_pinterest_search: Whether to search Pinterest for theme-matching pins (default True)
        user_id: ID of current user (injected by agent)
    
    Returns:
        JSON string with inspiration results including colors and composition ideas
    """
    results = []
    source = "suggestions"
    
    # Build a search query from theme and style
    search_query = theme
    if style:
        search_query = f"{theme} {style}"
    
    # First, try Pinterest search for themed inspiration
    if use_pinterest_search and not pinterest_board:
        # Add "painting" or "art" to improve results
        art_query = f"{search_query} painting art"
        pinterest_pins = search_pinterest_pins(art_query, limit=6)
        
        if pinterest_pins:
            source = "pinterest_search"
            for pin in pinterest_pins:
                results.append({
                    "title": pin.get("title", "Pinterest Pin"),
                    "pin_url": pin.get("pin_url", ""),
                    "source": "pinterest",
                })
    
    # If a board is provided, fetch from it (but note it won't be theme-filtered)
    if pinterest_board and not results:
        board_pins = fetch_pinterest_board(pinterest_board, limit=6)
        if board_pins:
            source = "pinterest_board"
            for pin in board_pins:
                results.append({
                    "title": pin.get("title", "Pinterest Pin"),
                    "pin_url": pin.get("pin_url", ""),
                    "source": "pinterest_board",
                    "note": "From your saved board (not filtered by theme)"
                })
    
    # If no Pinterest results, use fallback inspirations
    if not results:
        theme_lower = theme.lower()
        
        # Find matching fallback inspirations
        for key, inspirations in FALLBACK_INSPIRATIONS.items():
            if key in theme_lower:
                for insp in inspirations:
                    if style is None or style.lower() in insp.get("style", ""):
                        results.append({**insp, "source": "suggestion"})
        
        # Generate default if no matches
        if not results:
            results.append({
                "title": f"Inspiration for '{theme}'",
                "colors": generate_color_palette_suggestion(theme),
                "style": style or "varied",
                "suggestion": f"Explore '{theme}' with a mix of techniques and color approaches.",
                "source": "generated",
            })
    
    # Add suggested color palette based on theme
    suggested_colors = generate_color_palette_suggestion(theme)
    
    response = {
        "theme": theme,
        "source": source,
        "inspirations": results[:6],  # Limit to 6 results
        "suggested_palette": suggested_colors,
        "tip": "Click the links to view the full Pinterest images for reference.",
    }
    
    if pinterest_board and source != "pinterest_board":
        response["note"] = f"Could not fetch from Pinterest board '{pinterest_board}'. Showing search results instead."
    
    return json.dumps(response)
