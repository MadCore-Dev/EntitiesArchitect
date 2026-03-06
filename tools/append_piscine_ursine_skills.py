import json

SKILLS_PATH = '/Users/manojsamal/Documents/Projects/EntitiesArchitect/GameData/skills.json'

new_skills = {
  "Blood Frenzy": {
    "description": "Upon detecting the scent of fresh blood, the entity enters an involuntary, hyper-aggressive state. It ignores pain, attacks wildly, and prioritizes the bleeding target above all other threats.",
    "types": ["Passive", "Enhancement", "Rage"],
    "range": "Self",
    "mods": [
      { "target": "str", "op": "add", "expr": "4" },
      { "target": "natural_armor", "op": "subtract", "expr": "2" }
    ]
  },
  "Slippery": {
    "description": "Due to a thick secretion of aquatic mucus or oils, the entity is phenomenally difficult to hold onto. Attempts to grapple or restrain it suffer massive penalties.",
    "types": ["Passive", "Defense"],
    "range": "Self",
    "mods": [
      { "target": "evasion", "op": "add", "expr": "5" }
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
