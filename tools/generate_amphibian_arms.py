import urllib.request, json, sys, os

# Read prompt context
try:
    with open('/Users/manojsamal/Documents/Projects/EntitiesArchitect/LocalModel_Entity_Guide.md', 'r') as f:
        guide = f.read()
except Exception as e:
    print(f"Error reading guide: {e}")
    sys.exit(1)

prompt = f"{guide}\n\nTask: Generate the 'amphibian.json' file for generic Amphibian Arms (category: Appendages/arms). Provide 3 distinct variants. Return ONLY standard JSON."

data = {
    "model": "qwen2.5-coder:14b",
    "prompt": prompt,
    "stream": False,
    "options": {"num_ctx": 4096}
}

req = urllib.request.Request('http://127.0.0.1:11434/api/generate', data=json.dumps(data).encode('utf-8'))
req.add_header('Content-Type', 'application/json')

print("Sending request to local model qwen2.5-coder:14b ...")
try:
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode('utf-8'))
    reply = result.get('response', '')
    
    # Strip markdown formatting
    if "```" in reply:
        parts = reply.split("```")
        for p in parts:
            if p.startswith("json\n"):
                reply = p[5:]
                break
            elif p.startswith("{"):
                reply = p
                break
    reply = reply.strip()
    
    out_path = '/Users/manojsamal/Documents/Projects/EntitiesArchitect/GameData/Entities/Appendages/arms/amphibian.json'
    with open(out_path, 'w') as f:
        f.write(reply)
    print(f"Successfully generated and saved {out_path}")
    print("\nSAMPLE:\n" + reply[:500] + "...\n")
except Exception as e:
    print(f"Error reaching Ollama: {e}")

