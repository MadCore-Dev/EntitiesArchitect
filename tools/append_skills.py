import json, os

SKILLS_PATH = '/Users/manojsamal/Documents/Projects/EntitiesArchitect/GameData/skills.json'

new_skills = {
  "Bristle_Shed": {
    "description": "The entity violently rubs its hind legs against its abdomen, dislodging a cloud of barbed, urticating hairs into the air. These microscopic bristles penetrate the eyes and respiratory tracts of nearby foes, causing agonizing irritation and momentary blindness.",
    "types": ["Ranged_Attack", "Natural_Weapon", "Area_Of_Effect"],
    "range": "15ft",
    "mods": [
      { "target": "hp", "op": "subtract", "expr": "1d4", "damage_type": "Piercing" }
    ],
    "payloads": [
      { "id": "Blinded", "chance_per_tick": 0.4, "duration_ticks": 2 },
      { "id": "Irritated", "chance_per_tick": 0.6, "duration_ticks": 4 }
    ]
  },
  "Tremorsense": {
    "description": "Possesses hyper-sensitive tactile receptors or trichobothria hairs capable of detecting the exact origin and nature of any vibrations traveling through solid ground and structures.",
    "types": ["Passive", "Perception"],
    "range": "60ft_Surface",
    "mods": [
      { "target": "perception", "op": "add", "expr": "4" },
      { "target": "initiative", "op": "add", "expr": "3" }
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
except Exception as e:
    print(f"Error: {e}")
