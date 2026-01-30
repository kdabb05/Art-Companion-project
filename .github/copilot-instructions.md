# Art Studio Companion - AI Coding Instructions

## Project Overview
A web-based agentic application serving as a personal studio manager for artists. Features a stateful LLM agent with long-term memory, MCP tools, and a browser-based UI.

## Architecture
- **Backend:** Flask (Python)
- **Agent Framework:** Letta (tool calling + memory)
- **Database:** SQLite via SQLAlchemy
- **Frontend:** HTML + CSS + JavaScript (single-page app)
- **LLM Provider:** OpenRouter API
- **Package Manager:** uv (preferred)

## Directory Structure
```
Art-Companion-project/
├── backend/
│   ├── app.py              # Flask application entry point
│   ├── config.py           # Configuration (loads from .env)
│   ├── models/             # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── supply.py       # Supply inventory model
│   │   ├── project.py      # Project/session model
│   │   └── portfolio.py    # Artwork metadata model
│   ├── tools/              # MCP tool implementations
│   │   ├── __init__.py
│   │   ├── inspiration.py  # Pinterest/mock inspiration tool
│   │   ├── inventory.py    # Supply inventory manager
│   │   ├── portfolio.py    # Portfolio storehouse
│   │   └── project.py      # Project filesaver
│   └── agent/              # Letta agent configuration
│       ├── __init__.py
│       └── studio_agent.py # Agent setup and memory config
├── frontend/
│   ├── index.html          # Single-page app entry
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── app.js          # Main application logic
│       ├── chat.js         # Chat window handling
│       └── components.js   # Sidebar, gallery, panels
├── data/
│   └── studio.db           # SQLite database (gitignored)
├── .env                    # API keys (gitignored)
├── .env.example            # Template for required env vars
├── pyproject.toml          # uv/Python dependencies
└── README.md
```

## Environment Setup
```bash
# Install dependencies with uv
uv sync

# Required .env variables
OPENROUTER_API_KEY=your_key_here
LETTA_LLM_ENDPOINT=https://openrouter.ai/api/v1
LETTA_MODEL=anthropic/claude-3.5-sonnet  # or preferred model

# Run the application
uv run python backend/app.py
```

## Letta Agent Patterns
- **Agent initialization:** Create agent once at startup, reuse across requests
- **OpenRouter integration:** Configure Letta to use OpenRouter as the LLM backend
- **Tool registration:** Register all 4 MCP tools with the agent at initialization
- **Memory persistence:** Use Letta's archival memory for long-term facts, synced with SQLite
- **Conversation flow:** Each user message → agent.send_message() → tool calls → response

### Example Agent Setup
```python
from letta import create_client

client = create_client()
# Configure OpenRouter as LLM provider
agent = client.create_agent(
    name="studio_companion",
    llm_config={"model": "anthropic/claude-3.5-sonnet", "model_endpoint": os.getenv("LETTA_LLM_ENDPOINT")},
    tools=[inspiration_tool, inventory_tool, portfolio_tool, project_tool],
    system="You are an art studio companion that helps artists plan projects..."
)
```

### Tool Function Pattern
```python
def inventory_tool(action: str, item: dict = None) -> str:
    """
    Manage art supply inventory.
    action: 'list', 'add', 'update', 'low_stock'
    item: {brand, type, quantity} for add/update
    """
    # Implementation syncs with SQLite
    pass
```

## SQLAlchemy Models

### Supply Model
```python
class Supply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))  # paint, brush, canvas, etc.
    quantity = db.Column(db.Float, default=1.0)  # 0.0-1.0 for partial amounts
    unit = db.Column(db.String(20))  # tube, sheet, piece
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

### Project Model
```python
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='planning')  # planning, in_progress, completed
    description = db.Column(db.Text)
    steps = db.Column(db.JSON)  # [{step: 1, instruction: "...", completed: false}]
    supply_list = db.Column(db.JSON)  # [supply_id, ...]
    session_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

### Portfolio Model
```python
class Artwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image_path = db.Column(db.String(500), nullable=False)
    medium = db.Column(db.String(100))  # watercolor, oil, digital, etc.
    difficulty = db.Column(db.Integer)  # 1-5 scale
    date_created = db.Column(db.Date)
    notes = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## Flask API Routes

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/chat` | Send message to Letta agent, returns response |
| GET | `/api/supplies` | List all supplies |
| POST | `/api/supplies` | Add new supply |
| PUT | `/api/supplies/<id>` | Update supply quantity/details |
| GET | `/api/supplies/low-stock` | Get supplies with quantity < 0.3 |
| GET | `/api/projects` | List all projects |
| POST | `/api/projects` | Create new project |
| GET | `/api/projects/<id>` | Get project details with steps |
| PUT | `/api/projects/<id>` | Update project status/notes |
| GET | `/api/portfolio` | List all artworks |
| POST | `/api/portfolio` | Upload artwork with metadata |
| GET | `/api/portfolio/<id>` | Get artwork details |

## MCP Tools to Implement (4 total)
1. **Pinterest Inspiration Tool** - Fetch themed images/metadata for composition suggestions and color palettes
2. **Supply Inventory Manager** - CRUD for supplies with brand, type, quantity; includes "low stock" query
3. **Portfolio Storehouse** - Store artwork images with metadata (medium, date, difficulty, notes)
4. **Project Filesaver** - Save/resume project plans, step-by-step instructions, supply lists, session notes

## Long-Term Memory Pattern
Use Letta's built-in memory combined with SQLite persistence. Store:
- Supply inventory (brand, type, quantity)
- User preferences (mediums, styles, budget constraints)
- Project history with status
- Portfolio metadata

Memory must persist across sessions and inform agent responses.

## Frontend Components
- **Chat Window:** Central conversation area for agent interaction
- **Supply Sidebar:** Color-coded inventory (green=plenty, yellow=low, red=empty)
- **Projects Panel:** List saved projects with status; support resume flow
- **Portfolio Gallery:** Thumbnail grid with metadata
- **Quick Actions:** Scan Supplies, New Project, Show Low Stock, Get Inspiration

## Agent Behavior Conventions
- Always check inventory before proposing projects
- Respect budget constraints from user preferences
- Fetch inspiration before suggesting compositions
- Save project plans for later resumption
- For new users with empty data, ask clarifying questions or recommend starter supplies

## Testing Requirements
- **Scenario tests:** New user (empty memory) and returning user (with data)
- **Tool invocation:** Verify correct tools trigger for each action type
- **Persistence:** Data survives app restart
