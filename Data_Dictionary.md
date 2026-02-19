# MadCore RPG - Data Dictionary

This document defines the purpose, structure, and engine-level implementation details for every JSON collection in the `GameData/` directory.

---

## 1. Biomes (`World/biomes.json`)

**Purpose:** Defines the macro-ecosystems of the game world. Biomes act as environmental entities that can cast standard payloads (hazards), apply global passive modifiers (sensory impairments), determine terrain composition, and heavily mutate base creatures that spawn within them via weighted adaptation rules.

**Engine Implementation Notes:**
* The engine should treat the current Biome as an invisible "Entity" in the combat/simulation loop, capable of holding and processing its `payloads` array on a tick interval.
* The `adaptation_rules` are evaluated only once during entity generation/spawning.

**Schema Structure:**
* `id` (integer): Unique engine identifier.
* `name` (string): Display name.
* `description` (string): Flavor text utilized by UI and narrative log generators.
* `terrain_flags` (array of strings): Defines the physical makeup of the chunk. Maps directly to keys in `terrain_types.json`.
* `climate` (object):
  * `base_temp` (string): The standard temperature state.
  * `weather` / `night_temp` (string): Dynamic weather or night-time state shifts.
* `adaptation_rules` (object): Applied to base creatures generated in this biome.
  * `skills` (array of objects): `{ "id": "Skill_Name", "weight": int }`. Used in weighted random selection.
  * `mods` (array of objects): Standard engine modifiers using the `"expr"` logic. Includes an additional `"weight"` property.
* `payloads` (array of objects): Replaces hardcoded hazards. The environment attempts to cast these payloads globally on a tick interval. 
  * `{ "id": "Payload_Name", "chance_per_tick": float }`
* `sensory_mods` (array of objects): Standard engine modifiers applied to all entities currently inside the biome. Optionally uses a `"condition"` string.
* `resource_tags` (array of strings): Spawning tags for procedural generation (Flora/Geology).

**Example Entry:**
```json
"Arid_Desert": {
  "id": 4,
  "name": "Arid Desert",
  "description": "Endless oceans of shifting sand that bake beneath a merciless sun.",
  "terrain_flags": ["Sand", "Barren", "Flat"],
  "climate": { "base_temp": "Hot", "night_temp": "Freezing" },
  "adaptation_rules": {
    "skills": [ { "id": "Burrow", "weight": 70 } ],
    "mods": [ { "target": "con", "op": "add", "expr": "2", "weight": 100 } ]
  },
  "payloads": [
    { "id": "Sandstorm_Blind", "chance_per_tick": 0.05 },
    { "id": "Heatstroke", "chance_per_tick": 0.10 }
  ],
  "sensory_mods": [
    { "target": "sense_bonus", "op": "subtract", "expr": "1d4", "condition": "Mirage" }
  ],
  "resource_tags": ["Sandstone", "Cactus"]
}

---

## 2. Terrain Types (`Definitions/types_and_ranges/terrain_types.json`)

**Purpose:** Defines the mechanical rules, physical hazards, and strict procedural generation constraints for the map tiles of the game. These types are drawn from the `terrain_flags` palette provided by the active Biome.

**Engine Implementation Notes:**
* **Map Generation (Layering):** The engine constructs map tiles by selecting tags from the active Biome's palette. It uses the `category` property to assign layers, preventing physical impossibilities (e.g., ensuring a tile has exactly 1 `surface` and 1 `topography`, making it impossible to be both "Flat" and "Steep").
* **Map Generation (Mutual Exclusivity):** During tile construction, the engine must cross-reference the `excludes` array of every selected tag. If a collision is detected (e.g., "Magma" trying to spawn on a tile that already has "Shallow_Water"), the generator must reject the incompatible tag.
* **Traversal Checks:** If an entity stands on a terrain with a `required_traversal` (e.g., "Swim"), the engine must verify the entity possesses that traversal flag. If not, the engine should apply a severe failure state (e.g., paralyze movement, trigger drowning payloads).
* **Auras:** `mods` are applied as temporary, positional aura buffs/debuffs while the entity remains on that terrain tile.
* **Hazards:** `payloads` act as ground-based hazards (like stepping in Magma) evaluated on a tick interval.

**Schema Structure:**
* `category` (string): Defines the structural layer of the tile. Restricted enum: `"surface"`, `"topography"`, `"cover"`, `"condition"`, `"liquid"`, `"lighting"`.
* `description` (string): Flavor text utilized by UI and narrative log generators.
* `required_traversal` (string | null): Matches a flag from `traversal_types.json`.
* `excludes` (array of strings): A list of terrain keys that are mathematically forbidden from existing on the same map tile as this entry.
* `mods` (array of objects): Standard engine modifiers using the `"expr"` logic. Applied while an entity occupies the space. 
* `payloads` (array of objects): Standard environment hazard payloads triggered while in the space.
  * `{ "id": "Payload_Name", "chance_per_tick": float }`

**Example Entry:**
```json
"Magma": {
  "category": "liquid",
  "description": "Flowing liquid rock that incinerates anything it touches.",
  "required_traversal": null,
  "excludes": [
    "Aquatic", "Deep_Water", "Shallow_Water", "Ice", "Grass", 
    "Woodland", "Foliage", "Dense_Foliage", "Scrub", "Frozen_Earth"
  ],
  "mods": [
    {
      "target": "speed_bonus",
      "op": "multiply",
      "expr": "0.25"
    }
  ],
  "payloads": [
    {
      "id": "Extreme_Burn",
      "chance_per_tick": 1.0
    }
  ]
}
```

---

