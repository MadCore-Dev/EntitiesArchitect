import os
import json
import urllib.request
import urllib.error

# Configuration
ENTITIES_DIR = "/Users/manojsamal/Documents/Projects/EntitiesArchitect/GameData/Entities"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:14b" # Using the best 14B model available for creative writing

def generate_description(entity_name, entity_data):
    """Calls local Ollama API to generate a description for an entity."""
    
    # We strip out the old description if it exists so the model isn't biased,
    # or you can keep it as context. We'll strip it for a fresh take.
    data_for_prompt = {k: v for k, v in entity_data.items() if k != "description"}
    
    prompt = (
        f"You are a creative lore writer for a dark fantasy LitRPG game. "
        f"Write a rich, immersive, and flavorful description (1-3 sentences) for an entity component. "
        f"Focus on its biological, physical, or magical characteristics based on its stats and tags. "
        f"IMPORTANT: Respond ONLY with the description text itself. Do not include quotes, greetings, "
        f"or conversational filler like 'Here is the description'.\n\n"
        f"Component Name: {entity_name}\n"
        f"Component Data: {json.dumps(data_for_prompt, indent=2)}"
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
            # Optional: If you only want to overwrite empty descriptions or missing ones, 
            # you can add a check here. We are replacing all of them to get fresh AI lore.
            print(f"  -> Generating description for: {entity_name}...")
            
            new_desc = generate_description(entity_name, entity_data)
            
            if new_desc:
                # Clean up occasional quotes the model might still add
                new_desc = new_desc.strip('"').strip("'")
                
                entity_data['description'] = new_desc
                changes_made = True
                print(f"     [Success] {new_desc[:60]}...")
            else:
                print(f"     [Failed] Could not generate description.")

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
