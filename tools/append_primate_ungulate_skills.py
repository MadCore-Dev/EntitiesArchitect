import json

SKILLS_PATH = '/Users/manojsamal/Documents/Projects/EntitiesArchitect/GameData/skills.json'

new_skills = {
  "Complex_Problem_Solving": {
    "description": "Utilizing a massively expanded neocortex, the entity can dynamically analyze complex environments, rapidly identify weaknesses in enemy formations or structures, and devise multi-step tactical solutions on the fly.",
    "types": ["Action", "Enhancement"],
    "range": "Self",
    "mods": [
      { "target": "accuracy", "op": "add", "expr": "2" },
      { "target": "evasion", "op": "add", "expr": "2" }
    ],
    "combat_flags": ["Requires_LOS", "Ignores_Cover"]
  },
  "Tool Use": {
    "description": "The entity possesses the cognitive capacity and dexterous manipulators required to grip, wield, and invent complex implements, effectively treating found objects as highly lethal improvised weaponry.",
    "types": ["Action", "Enhancement"],
    "range": "Self",
    "mods": [
      { "target": "reach", "op": "add", "expr": "2" }
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
