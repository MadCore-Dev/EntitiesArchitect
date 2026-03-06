import json

SKILLS_PATH = '/Users/manojsamal/Documents/Projects/EntitiesArchitect/GameData/skills.json'

new_skills = {
  "Pheromone_Tracking": {
    "description": "Utilizes hyper-sensitive chemoreceptors (e.g. plumose antennae) to detect trace volatile chemicals in the air. Allows the entity to track targets perfectly over miles of open terrain.",
    "types": ["Action", "Enhancement"],
    "range": "Self",
    "mods": [
      { "target": "accuracy", "op": "add", "expr": "2" },
      { "target": "sense_bonus", "op": "add", "expr": "4" }
    ],
    "combat_flags": ["Ignores_Cover"]
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
