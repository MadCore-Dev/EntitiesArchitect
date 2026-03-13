import os
import json
import time
import urllib.request
import urllib.error

# Configuration
ENTITIES_DIR = "/Users/manojsamal/Documents/Projects/EntitiesArchitect/GameData/Entities"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:14b"  # 9GB — best creative/lore writer; fits fine in 24GB unified memory
SKIP_FILLED = True            # Set False to regenerate already-filled descriptions
CALL_DELAY_SEC = 0.1          # Minimal delay; 24GB unified memory handles back-to-back calls easily

def generate_description(entity_name, entity_data):
    """Calls local Ollama API to generate a description for an entity."""
    
    # We strip out the old description if it exists so the model isn't biased,
    # or you can keep it as context. We'll strip it for a fresh take.
    data_for_prompt = {k: v for k, v in entity_data.items() if k != "description"}
    
    # Build a concise version of data for the prompt (keep tags, grants_skills, mods summary)
    tags = data_for_prompt.get('tags', [])
    skills = data_for_prompt.get('grants_skills', [])
    mods = data_for_prompt.get('mods', [])
    stat_summary = ", ".join(f"{m['target']} {m['op']} {m['expr']}" for m in mods) if mods else "none"

    prompt = (
        f"You are a lore writer for a dark fantasy LitRPG game called Project Apotheosis. "
        f"Write a vivid, immersive description (1-3 sentences) for a creature body component. "
        f"Describe what it looks, feels, or behaves like — ground it in the tags and granted abilities. "
        f"IMPORTANT: Respond ONLY with the description text. No quotes, no greetings.\n\n"
        f"Component Name: {entity_name}\n"
        f"Tags: {', '.join(tags)}\n"
        f"Granted Skills: {', '.join(skills)}\n"
        f"Stat Changes: {stat_summary}"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7
        }
    }

    req = urllib.request.Request(OLLAMA_API_URL, data=json.dumps(payload).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response", "").strip()
    except urllib.error.URLError as e:
        print(f"  [!] Error connecting to Ollama: {e}")
        return None
    except json.JSONDecodeError:
        print(f"  [!] Error decoding JSON response from Ollama")
        return None


def process_json_file(file_path):
    print(f"\nProcessing file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"  [!] Skipping {file_path} - Invalid JSON")
        return

    changes_made = False

    for entity_name, entity_data in data.items():
        if isinstance(entity_data, dict):
            # Skip if description is already filled and SKIP_FILLED is True
            existing_desc = entity_data.get('description', '')
            if SKIP_FILLED and existing_desc and existing_desc.strip():
                print(f"  -- Skipping (already filled): {entity_name}")
                continue

            print(f"  -> Generating description for: {entity_name}...")

            new_desc = generate_description(entity_name, entity_data)

            if new_desc:
                # Clean up occasional quotes the model might still add
                new_desc = new_desc.strip('"').strip("'")

                entity_data['description'] = new_desc
                changes_made = True
                print(f"     [OK] {new_desc[:80]}...")
            else:
                print(f"     [FAIL] Could not generate description.")

            time.sleep(CALL_DELAY_SEC)  # Prevent memory pressure on M2

    if changes_made:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"  [+] Saved updates to {file_path}")


def main():
    print(f"Starting Entity Description Generation using {OLLAMA_MODEL}...")
    print(f"Target Directory: {ENTITIES_DIR}")
    
    if not os.path.exists(ENTITIES_DIR):
        print(f"Error: Directory {ENTITIES_DIR} does not exist.")
        return

    # Sequentially walk through all files
    for root, _, files in os.walk(ENTITIES_DIR):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                process_json_file(file_path)

    print("\nFinished processing all Entities.")

if __name__ == "__main__":
    main()
