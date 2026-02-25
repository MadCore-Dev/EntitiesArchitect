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

**2. Install the MadCore Dev Server extension**
```bash
bash tools/install_extension.sh
```

**3. Reload the Antigravity window**

`Cmd+Shift+P` → **Developer: Reload Window**

---

## Launching the Editor View

Once set up, open the **MadCore Dev Server** tab in the sidebar (⚡ icon).

1.  Find your `index.html` in the server list.
2.  Click **▶ Start** to spin up the local serving process.
3.  Click **🌐 Open** to view the tool in the Simple Browser.
4.  (Optional) Click **📱 QR** to view on your phone.

Drag the **Simple Browser** panel to the right editor group for the full split-screen layout:

```
┌─────────────────────┬──────────────────────┐
│  GameData/          │  MadCore Editor       │
│  Entity JSON files  │  (Simple Browser)     │
│                     │  Dynamic Port         │
└─────────────────────┴──────────────────────┘
```

---

## Project Customization

This project uses a `.madcore-server.json` file in the root to customize the dashboard branding. You can edit this file to change the title, subtitle, and theme colors.

```json
{
  "title": "Entities Architect",
  "subtitle": "Evolution Engine Dashboard",
  "themeColor": "#00d4aa"
}
```

---

## Running the Server Manually

The extension handles this automatically using Node.js, but you can still use the legacy Python script if needed:

```bash
python3 tools/serve_engine.py
# → MadCore Engine Server Running at http://localhost:8000
```

---

## Project Structure

```
EntitiesArchitect/
├── index.html                  ← Main data verification tool UI
├── madcore.schema.json         ← JSON schema for all GameData files
├── .madcore-server.json        ← Server dashboard branding
├── GameData/                   ← Entity data files (.json)
├── tools/
│   ├── serve_engine.py         ← Legacy HTTP server
│   ├── install_extension.sh    ← Installs the IDE extension
│   └── madcore-extension/      ← Extension source (Node-native)
│       ├── package.json
│       ├── extension.js
│       └── icon.svg
```

---

## VS Code Tasks

| Task | Action |
|---|---|
| ⚡ Open Dev Server | Select **Dashboard** in the sidebar |
| Start Engine Server | Press **Start** on the target file |
