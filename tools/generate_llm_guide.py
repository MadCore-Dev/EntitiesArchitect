import json, os

db = '/Users/manojsamal/Documents/Projects/EntitiesArchitect/gamedata.db'
base = '/Users/manojsamal/Documents/Projects/EntitiesArchitect/GameData'

def get_keys(path):
    p = os.path.join(base, path)
    if not os.path.exists(p): return []
    try:
        with open(p) as f:
            d = json.load(f)
            return list(d.keys()) if isinstance(d, dict) else d
    except: return []

skills = get_keys('skills.json')
b_stats = get_keys('Definitions/base_stats.json')
d_stats = get_keys('Definitions/derived_stats.json')
combat_tags = get_keys('Definitions/combat_tags.json')
trav = get_keys('Definitions/types_and_ranges/traversal_types.json')

with open('/Users/manojsamal/Documents/Projects/EntitiesArchitect/LocalModel_Entity_Guide.md', 'w') as f:
    f.write('# MadCore RPG: Strict Component Generation Guide\n\n')
    f.write('You are an expert game designer. Your task is to generate unique, mechanically distinct entity body parts (e.g., Arms, Legs, Tails) in strict JSON format.\n\n')
    
    f.write('## 1. Architectural Rules (CRITICAL)\n')
    f.write('- **Component Schema Match:** You must strictly follow the schema of `common.json` components.\n')
    f.write('- **Tags:** The `tags` array on a body part is open-ended (e.g., "Organic", "Scale", "Chitin", "Flesh"). These are used for flavor and procedural filtering.\n')
    f.write('- **Traversal:** The `traversal` array must contain ONLY valid items from `traversal_types.json` or "None".\n')
    f.write('- **Mods:** The `mods` array must use `{ "target": "stat_id", "op": "add|subtract|multiply", "val": float/int }`.\n')
    f.write('- **Skills (Crucial Constraint):** You may assign skills to `grants_skills`. However, if you use a skill that is NOT in the "Existing Skills List" below, you **MUST** also generate the JSON definition for that new skill at the bottom of your response in a separate JSON block.\n\n')
    
    f.write('## 2. Component JSON Schema Example\n')
    f.write('```json\n{\n  "Amphibian_Webbed_Arm": {\n')
    f.write('    "description": "Flavor text explaining its use.",\n')
    f.write('    "tags": ["Flesh", "Aquatic", "Slimy"],\n')
    f.write('    "traversal": ["Swim"],\n')
    f.write('    "mods": [\n      { "target": "dex", "op": "add", "val": 2 }\n    ],\n')
    f.write('    "grants_skills": ["Swim_Dash"]\n  }\n}\n```\n\n')
    
    f.write('## 3. Skill JSON Schema Example (Only if you invent a new skill)\n')
    f.write('```json\n{\n  "Swim_Dash": {\n')
    f.write('    "description": "A sudden burst of speed underwater.",\n')
    f.write('    "types": ["Movement"],\n')
    f.write('    "range": "Melee",\n')
    f.write('    "mods": [ { "target": "speed_bonus", "op": "add", "expr": "5" } ],\n')
    f.write('    "payloads": []\n  }\n}\n```\n\n')

    f.write('## 4. Valid Systems Vocabulary\n')
    f.write(f'- **Valid Base Stats (`target` in `mods`):** {", ".join(b_stats)}\n')
    f.write(f'- **Valid Derived Stats (`target` in `mods`):** {", ".join(d_stats)}\n')
    f.write(f'- **Valid Traversal Types (`traversal` array):** {", ".join(trav)}, None\n')
    
    f.write('## 5. Existing Skills List\n')
    f.write(f'Try to use these if they fit biologically: {", ".join(skills[:150])}\n\n')
    
    f.write('## 6. Your Task\n')
    f.write('I will give you an archetype and part (e.g., "arachnid legs").\n')
    f.write('Reply with the JSON for 3 to 5 variants of that part. If you granted any NEW skills not in the list, reply with a SECOND JSON block containing their skill definitions.\n')

print("Strict guide generated.")
