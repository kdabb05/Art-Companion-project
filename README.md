# Art Studio Companion 🎨

A web-based, agentic application designed to act as a personal studio manager for hobby and student artists.

## Quick Start

### Prerequisites
- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- An OpenRouter API key ([get one here](https://openrouter.ai/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kdabb05/Art-Companion-project.git
   cd Art-Companion-project
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   LETTA_MODEL=anthropic/claude-3.5-sonnet
   SECRET_KEY=your_secret_key_here
   ```

4. **Run the application**
   ```bash
   uv run python backend/app.py
   ```

5. **Open in browser**
   
   Navigate to [http://localhost:5000](http://localhost:5000)

### Using the App

1. **Get Started** - Click "Get Started" to use as a guest, or create an account to save your data
2. **Set Preferences** - Tell the AI about your art mediums (watercolor, crochet, knitting, etc.), styles, and goals
3. **Chat with the AI** - Ask for project ideas, manage your supplies, get inspiration
4. **Track Everything** - Manage supplies, projects, portfolio, and save ideas

---

## Overview

Art Studio Companion goes beyond a simple "chat with an LLM" to build a stateful AI agent that can remember your materials, preferences, and project history over time, and use that information to plan realistic, budget-aware art projects.

The AI agent can:

* Hold multi-step, natural conversations about creative ideas and constraints
* Call multiple tools to fetch inspiration, manage supplies, and save project data
* Maintain long-term memory about your supplies, preferences, and past projects

---

## Features

### Multi-User Support
- **Guest Mode**: Try the app without creating an account
- **User Accounts**: Create an account with username/password to persist your data
- **Conversation History**: All chats are saved and can be resumed later
- **Ideas Section**: Save and organize creative ideas from conversations

### Supported Art Forms
- Traditional painting (watercolor, acrylic, oil, gouache)
- Drawing (graphite, charcoal, colored pencil, ink, pastel)
- Digital art
- Fiber arts (crochet, knitting, embroidery)
- 3D arts (sculpting, ceramics)
- **Custom mediums** - add your own!

### AI Agent Capabilities
- Remembers your supplies, preferences, and project history
- Suggests projects based on what you have on hand
- Tracks supply levels and alerts when running low
- Provides themed inspiration and color palettes
- Saves step-by-step project plans

---

## Tech Stack

- **Backend**: Flask (Python 3.11+)
- **Database**: SQLite with SQLAlchemy ORM
- **AI**: OpenRouter API (Claude 3.5 Sonnet)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Auth**: Flask-Login with session-based authentication
- **Package Manager**: uv

---

## Project Structure

```
Art-Companion-project/
├── backend/
│   ├── app.py              # Flask application entry point
│   ├── config.py           # Configuration (loads from .env)
│   ├── models/             # SQLAlchemy models
│   │   ├── user.py         # User accounts and preferences
│   │   ├── supply.py       # Supply inventory
│   │   ├── project.py      # Project/session model
│   │   ├── portfolio.py    # Artwork metadata
│   │   ├── conversation.py # Chat history
│   │   └── idea.py         # Saved ideas
│   ├── tools/              # AI tool implementations
│   │   ├── inspiration.py  # Inspiration and color palettes
│   │   ├── inventory.py    # Supply inventory manager
│   │   ├── portfolio.py    # Portfolio storehouse
│   │   └── project.py      # Project filesaver
│   ├── routes/             # API route blueprints
│   │   ├── __init__.py     # Auth routes
│   │   ├── conversations.py
│   │   └── ideas.py
│   └── agent/              # AI agent configuration
│       └── studio_agent.py # OpenRouter integration
├── frontend/
│   ├── index.html          # Single-page app
│   ├── css/styles.css
│   └── js/
│       ├── auth.js         # Authentication handling
│       ├── app.js          # Main application logic
│       ├── chat.js         # Chat functionality
│       └── components.js   # UI components
├── data/
│   └── studio.db           # SQLite database (gitignored)
├── .env.example            # Template for environment variables
├── pyproject.toml          # Python dependencies
└── README.md
```

---

## API Endpoints

### Authentication
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/login` | Sign in with username |
| POST | `/api/auth/logout` | Sign out |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/onboarding` | Save preferences |

### Core Features
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/chat` | Send message to AI agent |
| GET/POST | `/api/supplies` | List/add supplies |
| GET/POST | `/api/projects` | List/create projects |
| GET/POST | `/api/portfolio` | List/add artworks |
| GET/POST | `/api/conversations` | List/create conversations |
| GET/POST | `/api/ideas` | List/save ideas |

---

## Example Conversations

**Managing Supplies:**
> "Add 3 skeins of Bernat Blanket yarn in Vintage White to my inventory"

**Planning Projects:**
> "I want to crochet a blanket for my living room. What do I need?"

**Getting Inspiration:**
> "Show me inspiration for a watercolor botanical painting"

**Tracking Progress:**
> "What supplies am I running low on?"

---

## Development

### Running in Development Mode
```bash
uv run python backend/app.py
```
The server runs with auto-reload enabled at `http://localhost:5000`.

### Running Tests
```bash
uv run pytest
```

### Resetting the Database
```bash
rm data/studio.db
uv run python backend/app.py  # Creates fresh database
```

---

## License

This project is for educational purposes.

---

## Acknowledgments

Built as a demonstration of agentic AI architecture with memory, tools, and a real UI.
