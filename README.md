# MadCore RPG — Entities Architect

A data-driven game engine workspace for designing and verifying RPG entity data. The IDE is configured as a **Game Engine Editor** — the data tool runs live inside the editor as a split-screen panel, similar to a Unity editor layout.

---

## Prerequisites

| Tool | Version |
|---|---|
| [Antigravity](https://antigravity.dev) | Latest |
| Python | 3.x |

> **Note:** VS Code also works, but the Activity Bar extension button requires Antigravity.

---

## Setup (First Time)

**1. Clone the repo**
```bash
git clone <your-repo-url>
cd EntitiesArchitect
```

**2. Install the MadCore Engine Launcher extension**
```bash
bash tools/install_extension.sh
```

**3. Reload the Antigravity window**

`Cmd+Shift+P` → **Developer: Reload Window**

---

## Launching the Editor View

Once set up, you have two ways to open the Game Engine View inside the IDE:

| Method | How |
|---|---|
| ⌨️ Keyboard shortcut | `⌘ + ⇧ + G` |
| 🎮 Activity Bar | Click the game controller icon in the left sidebar → **Open Editor View** |

The **Simple Browser** panel will open with the live data tool. Drag it to the right editor group for the full split-screen layout:

```
┌─────────────────────┬──────────────────────┐
│  GameData/          │  MadCore Editor       │
│  Entity JSON files  │  (Simple Browser)     │
│                     │  localhost:8000        │
└─────────────────────┴──────────────────────┘
```

---

## Running the Server Manually

The launcher auto-starts the server, but you can also run it directly:

```bash
python3 tools/serve_engine.py
# → MadCore Engine Server Running at http://localhost:8000
```

Then open `http://localhost:8000/index.html` in any browser.

---

## Project Structure

```
EntitiesArchitect/
├── index.html                  ← Main data verification tool UI
├── madcore.schema.json         ← JSON schema for all GameData files
├── GameData/                   ← Entity data files (.json)
├── tools/
│   ├── serve_engine.py         ← Local HTTP server (port 8000)
│   ├── install_extension.sh    ← Installs the IDE extension (run once)
│   └── madcore-extension/      ← Antigravity/VS Code extension source
│       ├── package.json
│       ├── extension.js
│       └── icon.svg
└── .vscode/
    ├── settings.json           ← JSON schema associations
    ├── tasks.json              ← Background server + launch tasks
    └── extensions.json         ← Recommended extensions
```

---

## VS Code Tasks

| Task | Shortcut |
|---|---|
| 🎮 Launch MadCore Editor | `Cmd+Shift+B` |
| Start Engine Server | `Ctrl+Shift+P` → Run Task |
