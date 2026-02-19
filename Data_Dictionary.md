# MadCore RPG - Data Dictionary

> **🏗️ ARCHITECTURE TODO / PENDING SYSTEMS**
> 
> **1. Materials & Items Dictionary**
> * **Observed In:** `World/biomes.json` (inside `resource_tags` like "Granite", "Iron_Ore", "Obsidian").
> * **Current State:** Acting as raw string keys for the procedural map generator to spawn nodes.
> * **Future Action:** Need to create `materials.json` or `items.json`. When a player mines "Iron_Ore", the engine needs this dictionary to know its weight, base value, crafting tags, and harvest difficulty.
> 
> **2. Contextual Conditions**
> * **Observed In:** `World/biomes.json` (inside `sensory_mods[].condition` like "Mirage", "Pitch Black", "Thick Smoke").
> * **Current State:** Acting as descriptive strings attached to modifier auras.
> * **Future Action:** Determine if these should remain as raw UI string labels, or if we need a `conditions.json` to formally define them as stackable environmental statuses (similar to `status_effects.json`).
> 
> ---

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

## 3. Temperature Bands (`World/temperature_bands.json`)

**Purpose:** Defines the baseline, persistent thermal state of a map chunk or Biome. It dictates standard environmental hazards and passive bodily stresses (like accelerated stamina drain in extreme heat) before any dynamic weather is applied.

**Engine Implementation Notes:**
* **Global Passive:** The `mods` array is applied to all entities within the chunk as a persistent, un-dodgeable aura.
* **Environmental Hazards:** The `payloads` array runs on the chunk's tick interval, attempting to cast status-inducing attacks (like "Heatstroke" or "Frostbite") on all valid targets in the zone.

**Schema Structure:**
* `description` (string): Flavor text for logs and UI.
* `mods` (array of objects): Standard engine modifiers using the `"expr"` logic.
* `payloads` (array of objects): Standard environment hazard payloads.
  * `{ "id": "Payload_Name", "chance_per_tick": float }`

**Example Entry:**
```json
"Extreme_Heat": {
  "description": "Lethal temperatures that can boil water in minutes.",
  "mods": [
    { "target": "stamina_regen", "op": "multiply", "expr": "0.5" },
    { "target": "water_retention", "op": "subtract", "expr": "2" }
  ],
  "payloads": [
    { "id": "Heatstroke", "chance_per_tick": 0.10 }
  ]
}

```

---

## 4. Weather Types (`World/weather_types.json`)

**Purpose:** Defines the dynamic, shifting meteorological events that overlay on top of a Biome's base state. Weather can dramatically alter combat via sensory impairments and can actively mutate the physical map by adding temporary terrain properties.

**Engine Implementation Notes:**

* **Dynamic Map Mutation:** When weather changes, the engine must read `terrain_additions` and temporarily append those tags to exposed tiles in the chunk (e.g., "Raining" dynamically adds the "Mud" tag to Dirt tiles).
* **Sensory Overrides:** The `sensory_mods` array acts as a global debuff to specific senses (like capping vision range during a Blizzard).
* **Active Hazards:** The `payloads` array adds immediate, volatile hazards (like Lightning Strikes or Sweeping Currents) on top of the base temperature hazards.

**Schema Structure:**

* `description` (string): Flavor text for logs and UI.
* `terrain_additions` (array of strings): Matches keys from `terrain_types.json`. Applied temporarily to the chunk's tiles while the weather is active.
* `sensory_mods` (array of objects): Standard engine modifiers using the `"expr"` logic, specifically targeting sensory stats (vision_range, hearing_range, etc.).
* `payloads` (array of objects): Standard environment hazard payloads.
* `{ "id": "Payload_Name", "chance_per_tick": float }`



**Example Entry:**

```json
"Blizzard": {
  "description": "A blinding storm of snow and ice.",
  "terrain_additions": ["Ice", "Slippery"],
  "sensory_mods": [
    { "target": "vision_range", "op": "multiply", "expr": "0.2" },
    { "target": "hearing_range", "op": "multiply", "expr": "0.4" }
  ],
  "payloads": [
    { "id": "Freezing_Wind", "chance_per_tick": 0.05 }
  ]
}

```

---