import json

SKILLS_PATH = '/Users/manojsamal/Documents/Projects/EntitiesArchitect/GameData/skills.json'

new_skills = {
  "Poison_Cloud": {
    "description": "The entity violently ruptures its spore caps or toxic glands, unleashing a billowing cloud of choking, necrotic gas in a wide radius that persists for several turns.",
    "types": ["Action", "Area_Of_Effect", "Damage"],
    "range": "Area",
    "mods": [
      { "target": "hp", "op": "subtract", "expr": "2d6", "damage_type": "Poison" }
    ],
    "payloads": [
      { "id": "Poisoned", "chance_per_tick": 0.8, "duration_ticks": 3 }
    ]
  },
  "Life_Drain": {
    "description": "Using invasive mycelial tendrils or vampiric magic, the entity siphons the literal life force of a grappled target, healing itself for the exact amount of damage dealt.",
    "types": ["Action", "Melee_Attack", "Healing"],
    "range": "Melee",
    "mods": [
      { "target": "hp", "op": "subtract", "expr": "1d8", "damage_type": "Necrotic" }
    ],
    "combat_flags": ["Vampiric_Heal"]
  },
  "Photosynthesis": {
    "description": "While standing in direct sunlight, the entity slowly processes solar radiation into usable metabolic energy, providing continuous passive, low-level cellular regeneration.",
    "types": ["Passive", "Healing"],
    "range": "Self",
    "mods": [
      { "target": "hp", "op": "add", "expr": "1", "condition": "In_Sunlight" }
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
