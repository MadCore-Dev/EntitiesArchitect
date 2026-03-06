#!/usr/bin/env python3
"""
MadCore Engine Server
Serves the project root over HTTP on port 8000.
Adds a POST /export-sqlite endpoint that receives the full GAME_DATA
JSON payload from the browser and writes gamedata.db to the project root.
"""

import http.server
import json
import os
import sqlite3
import socketserver
from urllib.parse import urlparse

PORT = 8000
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(ROOT_DIR, "gamedata.db")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def log_message(self, format, *args):
        pass  # suppress per-request noise

    # ── CORS pre-flight ──────────────────────────────────────────────────────
    def _send_cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors()
        self.end_headers()

    # ── POST handler ─────────────────────────────────────────────────────────
    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/export-sqlite":
            self._handle_export_sqlite()
        else:
            self.send_error(404)

    def _handle_export_sqlite(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        try:
            game_data = json.loads(body)
        except json.JSONDecodeError as e:
            self._json_response(400, {"ok": False, "error": f"Bad JSON: {e}"})
            return

        try:
            _write_sqlite(game_data)
        except Exception as e:
            self._json_response(500, {"ok": False, "error": str(e)})
            return

        self._json_response(200, {"ok": True, "path": DB_PATH})

    def _json_response(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type",   "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors()
        self.end_headers()
        self.wfile.write(body)


# ── SQLite writer ─────────────────────────────────────────────────────────────

def _write_sqlite(gd: dict):
    """
    Flatten GAME_DATA from the browser into a tidy gamedata.db.
    Tables created:
      base_stats       (id, displayName, description, spriteIcon, baseValue, statType)
      derived_stats    (id, displayName, description, spriteIcon, baseValue, formula)
      biomes           (id, data_json)
      status_effects   (id, data_json)
      behaviors        (id, data_json)
      weather_types    (id, data_json)
      entity_components(category, sub, id, data_json)   ← body part JSONs
    """
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    # ── base_stats ────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE base_stats (
            id TEXT PRIMARY KEY,
            displayName TEXT, description TEXT, spriteIcon TEXT,
            baseValue REAL, statType TEXT
        )
    """)
    for sid, s in (gd.get("base_stats") or {}).items():
        c.execute("INSERT OR REPLACE INTO base_stats VALUES (?,?,?,?,?,?)", (
            s.get("id", sid), s.get("displayName",""), s.get("description",""),
            s.get("spriteIcon",""), s.get("baseValue", 0.0), s.get("statType","Raw")
        ))

    # ── derived_stats ─────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE derived_stats (
            id TEXT PRIMARY KEY,
            displayName TEXT, description TEXT, spriteIcon TEXT,
            baseValue REAL, formula TEXT
        )
    """)
    for sid, s in (gd.get("derived_stats") or {}).items():
        formula = s.get("calculationFormula") or s.get("formula") or ""
        c.execute("INSERT OR REPLACE INTO derived_stats VALUES (?,?,?,?,?,?)", (
            sid, s.get("displayName",""), s.get("description",""),
            s.get("spriteIcon",""), s.get("baseValue", 0.0), formula
        ))

    # ── generic JSON blob tables ──────────────────────────────────────────────
    def _blob_table(table, source_dict):
        c.execute(f"CREATE TABLE {table} (id TEXT PRIMARY KEY, data_json TEXT)")
        for k, v in (source_dict or {}).items():
            c.execute(f"INSERT OR REPLACE INTO {table} VALUES (?,?)",
                      (k, json.dumps(v)))

    world    = gd.get("world") or {}
    mech     = gd.get("mechanics") or {}
    _blob_table("biomes",        world.get("biomes") or {})
    _blob_table("weather_types", world.get("weather_types") or {})
    _blob_table("status_effects",mech.get("status_effects") or {})
    _blob_table("behaviors",     mech.get("behaviors") or {})

    # ── entity body-part components ───────────────────────────────────────────
    c.execute("""
        CREATE TABLE entity_components (
            category TEXT, sub TEXT, id TEXT, data_json TEXT,
            PRIMARY KEY (category, sub, id)
        )
    """)
    bodies = gd.get("bodies") or {}
    for cat, sub_dict in bodies.items():
        for sub, parts in (sub_dict or {}).items():
            for pid, pdata in (parts or {}).items():
                c.execute(
                    "INSERT OR REPLACE INTO entity_components VALUES (?,?,?,?)",
                    (cat, sub, pid, json.dumps(pdata))
                )

    # ── skills ────────────────────────────────────────────────────────────────
    c.execute("CREATE TABLE skills (id TEXT PRIMARY KEY, data_json TEXT)")
    for k, v in (gd.get("skills") or {}).items():
        c.execute("INSERT OR REPLACE INTO skills VALUES (?,?)", (k, json.dumps(v)))

    conn.commit()
    conn.close()
    print(f"[export-sqlite] Wrote {DB_PATH}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"MadCore Engine Server → http://localhost:{PORT}")
        print(f"  /export-sqlite endpoint active — will write: {DB_PATH}")
        httpd.serve_forever()
