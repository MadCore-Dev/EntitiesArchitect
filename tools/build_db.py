import os, json, glob
from serve_engine import _write_sqlite

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GD_DIR = os.path.join(ROOT, "GameData")

def load_json(path):
    with open(path) as f: return json.load(f)

def build():
    gd = {
        "base_stats": load_json(os.path.join(GD_DIR, "Definitions/base_stats.json")),
        "derived_stats": load_json(os.path.join(GD_DIR, "Definitions/derived_stats.json")),
        "skills": load_json(os.path.join(GD_DIR, "skills.json")),
        "prefixes": load_json(os.path.join(GD_DIR, "prefixes.json")),
        "world": {
            "biomes": load_json(os.path.join(GD_DIR, "World/biomes.json")),
            "weather_types": load_json(os.path.join(GD_DIR, "World/weather_types.json")),
            "temperature_bands": load_json(os.path.join(GD_DIR, "World/temperature_bands.json")),
            "group_scaling": load_json(os.path.join(GD_DIR, "World/spawning_rules/group_scaling.json")),
            "size_limits": load_json(os.path.join(GD_DIR, "World/spawning_rules/size_limits.json"))
        },
        "mechanics": {
            "status_effects": load_json(os.path.join(GD_DIR, "Mechanics/status_effects.json")),
            "behaviors": load_json(os.path.join(GD_DIR, "Mechanics/behaviors.json"))
        },
        "variations": {
            "appearances": {
                "pigmentation": load_json(os.path.join(GD_DIR, "Entities/Core/appearance/pigmentation.json")),
                "patterns": load_json(os.path.join(GD_DIR, "Entities/Core/appearance/patterns.json"))
            },
            "biological_upgrades": load_json(os.path.join(GD_DIR, "Mechanics/biological_upgrades.json")),
            "size_indices": load_json(os.path.join(GD_DIR, "Mechanics/growth_stages/size_indices.json"))
        },
        "loot": {
            "anatomy_drops": load_json(os.path.join(GD_DIR, "Mechanics/anatomy_drops.json")),
            "harvest_types": load_json(os.path.join(GD_DIR, "Mechanics/harvest_types.json")),
            "loot_quality": load_json(os.path.join(GD_DIR, "Mechanics/loot_quality.json"))
        },
        "definitions": {
            "damage_types": load_json(os.path.join(GD_DIR, "Definitions/types_and_ranges/damage_types.json")),
            "skill_types": load_json(os.path.join(GD_DIR, "Definitions/types_and_ranges/skill_types.json")),
            "terrain_types": load_json(os.path.join(GD_DIR, "Definitions/types_and_ranges/terrain_types.json")),
            "traversal_types": load_json(os.path.join(GD_DIR, "Definitions/types_and_ranges/traversal_types.json")),
            "vision_types": load_json(os.path.join(GD_DIR, "Definitions/types_and_ranges/vision_types.json")),
            "hearing_types": load_json(os.path.join(GD_DIR, "Definitions/types_and_ranges/hearing_types.json")),
            "scent_types": load_json(os.path.join(GD_DIR, "Definitions/types_and_ranges/scent_types.json")),
            "combat_tags": load_json(os.path.join(GD_DIR, "Definitions/combat_tags.json")),
            "consumable_categories": load_json(os.path.join(GD_DIR, "consumable_categories.json"))
        },
        "bodies": {}
    }

    # Bodies 
    for comp_type in ["Appendages", "Cephalon", "Core", "Flora", "Geological"]:
        comp_dir = os.path.join(GD_DIR, "Entities", comp_type)
        if not os.path.exists(comp_dir): continue
        for sub in os.listdir(comp_dir):
            sub_dir = os.path.join(comp_dir, sub)
            if not os.path.isdir(sub_dir) or sub == "appearance": continue
            
            cat_key = comp_type.lower()
            if cat_key == "geological": cat_key = "geology"
            
            if cat_key not in gd["bodies"]: gd["bodies"][cat_key] = {}
            if sub not in gd["bodies"][cat_key]: gd["bodies"][cat_key][sub] = {}
            
            for file in glob.glob(os.path.join(sub_dir, "*.json")):
                data = load_json(file)
                if isinstance(data, dict):
                    gd["bodies"][cat_key][sub].update(data)

    _write_sqlite(gd)
    print("Direct offline build successful!")

if __name__ == "__main__":
    build()
