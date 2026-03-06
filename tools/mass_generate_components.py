import urllib.request, json, sys, os

DB_DIR = '/Users/manojsamal/Documents/Projects/EntitiesArchitect/GameData'
SKILLS_PATH = os.path.join(DB_DIR, 'skills.json')
GUIDE_PATH = '/Users/manojsamal/Documents/Projects/EntitiesArchitect/LocalModel_Entity_Guide.md'

LINEAGES = ['arachnid', 'avian', 'saurian', 'insect', 'primate', 'feline', 'canine', 'amphibian', 'construct', 'fungal', 'plant', 'piscine', 'ungulate', 'ursine']
CATEGORIES = ['Appendages/arms', 'Appendages/legs', 'Appendages/tails', 'Appendages/wings', 'Appendages/fins', 'Appendages/tentacles', 'Cephalon/cranium', 'Cephalon/ears', 'Cephalon/eyes', 'Cephalon/maw', 'Cephalon/nose', 'Core/chassis', 'Core/integument']

def get_keys(rel_path):
    p = os.path.join(DB_DIR, rel_path)
    if not os.path.exists(p): return []
    try:
        with open(p, 'r') as f:
            d = json.load(f)
            return list(d.keys()) if isinstance(d, dict) else d
    except: return []

def update_guide():
    """Reads the precise exact keys from Definitions and updates the markdown guide so the LLM knows the rules for this exact moment."""
    skills_keys = get_keys('skills.json')
    combat_tags = get_keys('Definitions/combat_tags.json')
    vision = get_keys('Definitions/types_and_ranges/vision_types.json')
    hearing = get_keys('Definitions/types_and_ranges/hearing_types.json')
    scent = get_keys('Definitions/types_and_ranges/scent_types.json')
    traversal = get_keys('Definitions/types_and_ranges/traversal_types.json')
    
    sensory = vision + hearing + scent

    with open(GUIDE_PATH, 'w') as f:
        f.write('# MadCore RPG: Strict Component Generation Guide\n\n')
        f.write('You are an expert game designer. Generate unique, mechanically distinct entity body parts in strict JSON format.\n\n')
        
        f.write('## 1. Architectural Rules (CRITICAL)\n')
        f.write('- **Component Schema:** You must output a JSON dictionary where keys are the specific part name.\n')
        f.write('- **Tags:** The `tags` array on a body part must contain open ended strings describing its biological/material makeup AND any sensory capacities (e.g. "Flesh", "Scale", "Echolocation").\n')
        f.write('- **Traversal:** The `traversal` array must contain ONLY Exact valid strings from the allowed traversal list.\n')
        f.write('- **Mods:** The `mods` array must use `{ "target": "stat_id", "op": "add|subtract|multiply", "val": float/int }`.\n')
        f.write('- **Skills:** Try to use existing skills from the list. If you invent a new skill, you MUST output a second JSON block at the bottom containing its definition.\n\n')
        
        f.write('## 2. Valid Systems Vocabulary (EXACT STRINGS ONLY)\n')
        f.write(f'- **Valid Combat Tags:** {", ".join(combat_tags)}\n')
        f.write(f'- **Valid Traversal Types (`traversal` array):** {", ".join(traversal)}\n')
        f.write(f'- **Valid Sensory Tags (put in `tags` array):** {", ".join(sensory)}\n\n')
        
        f.write('## 3. Existing Skills List\n')
        f.write(f'Try to use these if they fit biologically: {", ".join(skills_keys[:200])}...\n\n')
        
        f.write('## 4. Output Format\n')
        f.write('Output precisely TWO JSON blocks (wrapped in ```json). Block 1: The components. Block 2: The novel skills you invented (or an empty {} if none).\n')

def add_new_skills(new_skills_dict):
    if not new_skills_dict: return
    with open(SKILLS_PATH, 'r') as f:
        master_skills = json.load(f)
    
    added = 0
    for k, v in new_skills_dict.items():
        if k not in master_skills:
            master_skills[k] = v
            added += 1
            
    if added > 0:
        with open(SKILLS_PATH, 'w') as f:
            json.dump(master_skills, f, indent=2)
        print(f"  [+] Injected {added} new unique skills into skills.json!")

def call_llm(lineage, category):
    prompt_text = f"Task: Generate the '{lineage}.json' file for generic {lineage.capitalize()} {category.split('/')[-1].capitalize()} (category: {category}). Provide 3 distinct variants. Remember to output 2 json blocks!"
    
    try:
        with open(GUIDE_PATH, 'r') as f:
            guide = f.read()
    except: return None, None
    
    data = {
        "model": "qwen2.5-coder:14b",
        "prompt": f"{guide}\n\n{prompt_text}",
        "stream": False,
        "options": {"num_ctx": 4096, "temperature": 0.7}
    }
    
    req = urllib.request.Request('http://127.0.0.1:11434/api/generate', data=json.dumps(data).encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        reply = result.get('response', '')
        
        # Parse output for 2 JSON blocks
        blocks = []
        if "```" in reply:
            parts = reply.split("```")
            for p in parts:
                if p.startswith("json\n"):
                    blocks.append(p[5:].strip())
        
        comps = json.loads(blocks[0]) if len(blocks) > 0 else {}
        skills = json.loads(blocks[1]) if len(blocks) > 1 else {}
        return comps, skills
    except Exception as e:
        print(f"  [!] Failed LLM call: {e}")
        return None, None

def main():
    print("Initiating Mass Component Generation Flow...")
    for lin in LINEAGES:
        for cat in CATEGORIES:
            out_file = os.path.join(DB_DIR, 'Entities', cat, f"{lin}.json")
            
            # Skip if file exists and has actual data populated
            needs_gen = True
            if os.path.exists(out_file):
                try:
                    with open(out_file, 'r') as f:
                        data = json.load(f)
                        if data and len(data) > 0:
                            needs_gen = False
                except:
                    pass
            
            if not needs_gen:
                continue
                
            print(f"Generating {lin} / {cat} ...")
            
            # 1. Update the robust guide so the LLM has the exact up-to-date DB state
            update_guide()
            
            # 2. Call the LLM
            comps, new_skills = call_llm(lin, cat)
            
            # 3. Save the components
            if comps:
                os.makedirs(os.path.dirname(out_file), exist_ok=True)
                with open(out_file, 'w') as f:
                    json.dump(comps, f, indent=2)
                print(f"  [v] Wrote {out_file}")
                
                # 4. Inject the new skills
                add_new_skills(new_skills)

if __name__ == '__main__':
    main()
