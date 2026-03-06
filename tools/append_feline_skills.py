import json

SKILLS_PATH = '/Users/manojsamal/Documents/Projects/EntitiesArchitect/GameData/skills.json'

new_skills = {
  "Throat_Clamp": {
    "description": "The entity locks its short, massive jaws directly onto the target's trachea. While grappling, the target slowly suffocates, unable to scream or breathe, while the entity waits for them to expire.",
    "types": ["Action", "Melee_Attack", "Grapple"],
    "range": "Melee",
    "mods": [
      { "target": "hp", "op": "subtract", "expr": "1d6", "damage_type": "Asphyxiation" }
    ],
    "payloads": [
      { "id": "Grappled", "chance_per_tick": 0.9, "duration_ticks": 2 },
      { "id": "Silenced", "chance_per_tick": 1.0, "duration_ticks": 1 }
    ]
  }
}

try:
    with open(SKILLS_PATH, 'r') as f:
        data = json.load(f)
    for k, v in new_skills.items():
        if k not in data:
            data[k] = v
            print(f"Added {k}")
    with open(SKILLS_PATH, 'w') as f:
        json.dump(data, f, indent=2)
except Exception: pass
