import json, os

SKILLS_PATH = '/Users/manojsamal/Documents/Projects/EntitiesArchitect/GameData/skills.json'

new_skills = {
  "Muffled_Flight": {
    "description": "The entity possesses specialized down and fringed feathers that acoustically dampen all sound produced by its wingbeats. It can approach prey from the air in absolute, terrifying silence.",
    "types": ["Passive", "Enhancement"],
    "range": "Melee",
    "mods": [
      { "target": "stealth", "op": "add", "expr": "4" }
    ]
  },
  "Target_Lock": {
    "description": "Utilizing foveal concentration, the entity locks its gaze onto a single target from extreme distances, drastically increasing its accuracy when diving or lunging to strike.",
    "types": ["Action", "Enhancement"],
    "range": "100ft",
    "mods": [
      { "target": "accuracy", "op": "add", "expr": "3" }
    ],
    "combat_flags": ["Requires_LOS"]
  },
  "Dive": {
    "description": "The entity folds its wings into a high-speed aerodynamic stoop, converting altitude entirely into terminal velocity before striking with its talons. The terrifying acceleration severely reduces the target's ability to evade.",
    "types": ["Action", "Melee_Attack"],
    "range": "100ft",
    "mods": [
      { "target": "hp", "op": "subtract", "expr": "2d6 + dex", "damage_type": "Bludgeoning" }
    ],
    "payloads": [
      { "id": "Prone", "chance_per_tick": 0.6, "duration_ticks": 2 }
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
except Exception as e:
    print(f"Error: {e}")
