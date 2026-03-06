import json, os

SKILLS_PATH = '/Users/manojsamal/Documents/Projects/EntitiesArchitect/GameData/skills.json'

new_skills = {
  "Toxic_Secretion": {
    "description": "Upon taking physical damage, heavily modified parotoid glands violently rupture, coating the entity in a milky, virulent bufotoxin. Any creature grappling or biting the user suffers intense chemical burns.",
    "types": ["Passive", "Reaction"],
    "range": "Melee",
    "mods": [
      { "target": "hp", "op": "subtract", "expr": "1d6", "damage_type": "Acid" }
    ],
    "payloads": [
      { "id": "Poisoned", "chance_per_tick": 0.5, "duration_ticks": 3 }
    ]
  },
  "Aquatic_Respiration": {
    "description": "The entity possesses feathery external gills optimized for extracting dissolved oxygen directly from water, allowing indefinite submersion without holding breath.",
    "types": ["Passive", "Enhancement"],
    "range": "Melee",
    "mods": [
      { "target": "water_retention", "op": "add", "expr": "5" }
    ]
  },
  "Tongue_Lash": {
    "description": "A split-second, hydraulic launch of a sticky, prehensile tongue. Capable of snatching small prey or violently pulling an opponent off balance from a distance.",
    "types": ["Ranged_Attack", "Natural_Weapon", "Grapple"],
    "range": "15ft",
    "mods": [
      { "target": "hp", "op": "subtract", "expr": "1d4", "damage_type": "Bludgeoning" }
    ],
    "payloads": [
      { "id": "Grappled", "chance_per_tick": 0.8, "duration_ticks": 1 },
      { "id": "Pulled", "chance_per_tick": 0.5, "duration_ticks": 1 }
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
