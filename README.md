# Art-Companion-project

## Overview

Art Studio Companion is a web-based, agentic application designed to act as a personal studio manager for hobby and student artists. The goal of the project is to go beyond a simple “chat with an LLM” and instead build a stateful AI agent that can remember a user’s materials, preferences, and project history over time, and use that information to plan realistic, budget-aware art projects.

At its core, the application will feature an LLM-based agent that can:

* Hold multi-step, natural conversations about creative ideas and constraints.
* Call multiple MCP tools to fetch inspiration, manage supplies, and save project data.
* Maintain long-term memory about the user’s supplies, preferences, and past projects.

The application is intended to feel like a long-term studio companion rather than a one-off chat session.

---

## Target Users

The primary users are:

* Hobby artists who want help organizing their materials and planning manageable projects.
* Student artists who want structured project guidance and a lightweight portfolio tracker.
* Myself, as a test user, for iterating on agent behavior and long-term personalization.

The system is not required to be commercially practical; its primary purpose is to demonstrate an ambitious, agentic architecture with memory, tools, and a real UI.

---

## Core Agent Capabilities

The LLM-based agent will be designed to:

* Maintain conversational context across multiple turns.

* Remember long-term information such as:

  * Supply inventory
  * Favorite mediums and styles
  * Budget constraints
  * Project history
  * Portfolio metadata

* Perform tool-driven reasoning, for example:

  * Inspecting inventory before proposing a project
  * Fetching visual inspiration before suggesting compositions
  * Saving project plans and session notes for later resumption

The agent will adapt over time to the user’s evolving preferences (e.g., “bold color,” “loose brushwork,” “1-hour weeknight sessions”).

---

## MCP Tools (4 Planned)

The agent will be extended using multiple MCP tools. At least three are required for the course; this project proposes four.

### 1. Pinterest Inspiration Tool

Given a theme (e.g., “botanical watercolor,” “moody cityscape”), this tool will fetch curated images and metadata from Pinterest or a mock API.

The agent will use this tool to:

* Suggest compositions
* Extract color palettes
* Propose visual references

---

### 2. Supply Inventory Manager

This tool will:

* Track supplies with brand, type, and quantity

  * Example: “Winsor & Newton Cadmium Yellow, half tube remaining”
* Support adding, updating, and listing supplies
* Provide a “low stock” query

This enables supply-aware project planning and budget-conscious suggestions.

---

### 3. Portfolio Storehouse

This tool will:

* Store uploaded images of finished or in-progress artwork
* Attach metadata such as:

  * Medium
  * Date
  * Difficulty
  * Notes

The agent will use portfolio history to learn the user’s evolving style and preferences.

---

### 4. Project Filesaver

This tool will:

* Save detailed project plans
* Store step-by-step instructions
* Track supply lists and session notes

It will allow the user to pause a project and later ask the agent to resume from where they left off.

---

## Web Interface

The application will provide a simple browser-based GUI with the following components:

### Chat Window

* Central conversation area where the user describes ideas and constraints.
* The agent responds with:

  * Project plans
  * Inspiration
  * Inventory-aware suggestions

---

### Supply Status Sidebar

A color-coded inventory view:

* Green: plenty
* Yellow: running low
* Red: empty

This gives quick visibility into available materials.

---

### Projects Panel

* List of saved projects with titles and status (e.g., “in progress,” “completed”).
* Clicking a project will load its notes and allow the agent to continue planning or execution.

---

### Portfolio Gallery

* Thumbnail grid of uploaded artwork
* Basic metadata display
* Used to review progress and evolving style

---

### Quick Actions

* Scan Supplies: upload a photo of supplies and infer inventory items (initially basic).
* New Project: start a new AI-assisted project planning flow.
* Show Low Stock: quickly view items that need restocking.
* Get Inspiration: trigger an inspiration-finding flow.

---

## Long-Term Memory

The agent will use a combination of:

* Letta’s built-in memory
* SQLite-based persistent storage

Long-term memory will store:

* Supply inventory
* Style and medium preferences
* Budget constraints
* Project history
* Portfolio metadata

This memory will be reloaded across sessions so the agent can behave consistently over time.

---

## Architecture (Planned)

**Backend:** Flask (Python)

**Agent Framework:** Letta (LLM agent with tool calling and memory)

**Database:** SQLite (via SQLAlchemy)

**Frontend:** HTML + CSS + JavaScript (single-page style UI)

The agent will run as a service that receives user messages, performs reasoning, invokes tools as needed, and returns structured responses to the frontend.

---

## Testing & Evaluation Plan

To verify the application behaves as intended:

### Scenario Tests

* New user with empty memory:

  * Ask for a project and confirm the agent either recommends starter supplies or asks clarifying questions.

* Returning user with inventory and portfolio data:

  * Ask for a project under a budget and confirm the agent respects known supplies and price constraints.

---

### Tool Invocation Tests

* Confirm that planning a project triggers:

  * Inspiration tool
  * Inventory tool
  * Project saving tool

* Confirm “Show low stock” only queries inventory and renders the correct status.

---

### Persistence Checks

* Add supplies, projects, and portfolio pieces.
* Restart the app.
* Confirm that all data is still present and used by the agent.

---

## Roadmap / Stretch Features

* “Inspiration Network” of art friends or mentors with distinct style profiles.
* More robust image-to-inventory recognition for scanned supply photos.
* Deeper portfolio analytics (e.g., tracking most-used mediums, colors, or themes).
* Optional deployment to a serverless platform (e.g., modal.com) for easier sharing.

---

## Why This Project Is Ambitious

This project combines:

* A stateful LLM-based agent
* Multiple MCP tools
* Long-term memory
* A real GUI
* Persistent storage
* Multi-step, tool-driven reasoning

The goal is not to produce a minimal demo, but to build a genuinely agentic application that evolves with its user over time. It is significantly more complex than a simple “chat with an LLM” interface and is designed to stretch both technical and conceptual boundaries for the course project.
