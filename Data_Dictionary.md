# MadCore RPG - Data Dictionary

This document defines the purpose, structure, and engine-level implementation details for every JSON collection in the `GameData/` directory.

## 1. Biomes (`World/biomes.json`)

**Purpose:** Defines the macro-ecosystems of the game world. Biomes act as environmental entities that can cast standard payloads (hazards and sensory auras), determine terrain composition, and heavily mutate base creatures that spawn within them via weighted adaptation rules.

**Engine Implementation Notes:**

* The engine should treat the current Biome as an invisible "Entity" in the combat/simulation loop, capable of holding and processing its `payloads` array on a tick interval.

* Environmental auras (like reduced vision from thick smoke) are applied by defining a Payload with a `chance_per_tick: 1.0`, effectively acting as a constant, blockable status effect.

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

* `payloads` (array of objects): Environmental hazards and sensory auras. The environment attempts to cast these payloads globally on a tick interval.

  * `{ "id": "Payload_Name", "chance_per_tick": float }`

* `resource_tags` (array of strings): Spawning tags for procedural generation (Flora/Geology).

**Example Entry:**

"Arid_Desert": {
  "id": 4,
  "name": "Arid Desert",
  "description": "Endless oceans of shifting sand that bake beneath a merciless sun.",
  "terrain_flags": ["Sand", "Barren", "Flat", "Rock", "Dirt", "Uneven"],
  "climate": { "base_temp": "Hot", "night_temp": "Freezing" },
  "adaptation_rules": {
    "skills": [ { "id": "Burrow", "weight": 70 } ],
    "mods": [ { "target": "con", "op": "add", "expr": "2", "weight": 100 } ]
  },
  "payloads": [
    { "id": "Sandstorm_Blind", "chance_per_tick": 0.05 },
    { "id": "Heatstroke", "chance_per_tick": 0.10 },
    { "id": "Mirage", "chance_per_tick": 1.0 }
  ],
  "resource_tags": ["Sandstone", "Cactus", "Dry_Brush", "Glass"]
}


## 2. Terrain Types (`Definitions/types_and_ranges/terrain_types.json`)

**Purpose:** Defines the mechanical rules, physical hazards, and strict procedural generation constraints for the map tiles of the game. These types are drawn from the `terrain_flags` palette provided by the active Biome.

**Engine Implementation Notes:**

* **Map Generation (Layering):** The engine constructs map tiles by selecting tags from the active Biome's palette. It uses the `category` property to assign layers, preventing physical impossibilities (e.g., ensuring a tile has exactly 1 `surface` and 1 `topography`, making it impossible to be both "Flat" and "Steep").

* **Map Generation (Mutual Exclusivity):** During tile construction, the engine must cross-reference the `excludes` array of every selected tag. If a collision is detected, the generator must reject the incompatible tag.

* **Traversal Checks:** If an entity stands on a terrain with a `required_traversal` (e.g., "Swim"), the engine must verify the entity possesses that traversal flag. If not, apply a failure state.

* **Auras & "Everything is a Payload":** Strict architectural rule: continuous buffs/debuffs from terrain are *not* handled via naked `mods`. Instead, terrain must trigger a payload with `"chance_per_tick": 1.0` that casts an ambient Status Effect (e.g., `Terrain_Magma_Drag`).

* **Hazards:** `payloads` act as ground-based hazards (like stepping in Magma) evaluated on a tick interval.

**Schema Structure:**

* `category` (string): Defines the structural layer of the tile. Restricted enum: `"surface"`, `"topography"`, `"cover"`, `"condition"`, `"liquid"`, `"lighting"`.

* `description` (string): Flavor text utilized by UI and narrative log generators.

* `required_traversal` (string | null): Matches a flag from `traversal_types.json`.

* `excludes` (array of strings): A list of terrain keys that are mathematically forbidden from existing on the same map tile.

* `mods` (array of objects): Strictly kept empty (`[]`) for runtime terrain elements to preserve payload architecture.

* `payloads` (array of objects): Environmental hazards and ambient statuses triggered while in the space.

  * `{ "id": "Payload_Name", "chance_per_tick": float }`

**Example Entry:**

"Magma": {
  "category": "liquid",
  "description": "Flowing liquid rock that incinerates anything it touches.",
  "required_traversal": null,
  "excludes": [
    "Aquatic", "Deep_Water", "Shallow_Water", "Ice", "Grass", 
    "Woodland", "Foliage", "Dense_Foliage", "Scrub", "Frozen_Earth"
  ],
  "mods": [],
  "payloads": [
    {
      "id": "Terrain_Magma_Drag",
      "chance_per_tick": 1.0
    },
    {
      "id": "Extreme_Burn",
      "chance_per_tick": 1.0
    }
  ]
}


## 3. Temperature Bands (`World/temperature_bands.json`)

**Purpose:** Defines the baseline, persistent thermal state of a map chunk or Biome. It dictates standard environmental hazards and passive bodily stresses (like accelerated stamina drain in extreme heat).

**Engine Implementation Notes:**

* **Global Passive ("Everything is a Payload"):** Thermal states do not possess direct modifiers. Instead, they apply their continuous mathematical stresses by casting an ambient Status Effect payload with `"chance_per_tick": 1.0` (e.g., `Ambient_Extreme_Heat`).

* **Environmental Hazards:** The `payloads` array also runs secondary checks on the chunk's tick interval to cast spike hazards (like "Heatstroke" or "Frostbite").

**Schema Structure:**

* `description` (string): Flavor text for logs and UI.

* `mods` (array of objects): Strictly kept empty (`[]`) for runtime elements.

* `payloads` (array of objects): Ambient statuses and environment hazard payloads.

  * `{ "id": "Payload_Name", "chance_per_tick": float }`

**Example Entry:**

"Extreme_Heat": {
  "description": "Lethal temperatures that can boil water in minutes.",
  "mods": [],
  "payloads": [
    { "id": "Ambient_Extreme_Heat", "chance_per_tick": 1.0 },
    { "id": "Heatstroke", "chance_per_tick": 0.10 }
  ]
}


## 4. Weather Types (`World/weather_types.json`)

**Purpose:** Defines the dynamic, shifting meteorological events that overlay on top of a Biome's base state. Weather can dramatically alter combat via sensory impairments and actively mutate the physical map.

**Engine Implementation Notes:**

* **Dynamic Map Mutation:** When weather changes, the engine reads `terrain_additions` and temporarily appends those tags to exposed tiles in the chunk (e.g., "Raining" adds "Mud").

* **Sensory Overrides & Hazards:** The `payloads` array handles both volatile hazards (Lightning Strikes) and persistent sensory debuffs (Blizzard Blindness) configured with `"chance_per_tick": 1.0`.

**Schema Structure:**

* `description` (string): Flavor text for logs and UI.

* `terrain_additions` (array of strings): Matches keys from `terrain_types.json`.

* `payloads` (array of objects): Hazards and sensory auras.

  * `{ "id": "Payload_Name", "chance_per_tick": float }`

**Example Entry:**

"Blizzard": {
  "description": "A blinding storm of snow and ice.",
  "terrain_additions": ["Ice", "Slippery"],
  "payloads": [
    { "id": "Freezing_Wind", "chance_per_tick": 0.05 },
    { "id": "Blizzard_Blindness", "chance_per_tick": 1.0 },
    { "id": "Storm_Deafness", "chance_per_tick": 1.0 }
  ]
}


## 5. Traversal Types (`Definitions/types_and_ranges/traversal_types.json`)

**Purpose:** Defines the physical or magical methods an entity uses to navigate the game world.

**Engine Implementation Notes:**

* **Bitmask Architecture:** Parsed into a `uint64_t traversalFlags` bitmask.

* **Terrain Interlocking:** When entering a tile with a `required_traversal`, the engine must do a bitwise `AND` check against the entity's flags.

* **Physics Automation:** If an environmental payload (e.g., "Trip_And_Fall") attempts to cast on the entity, the engine checks the `payload_immunities` array to bypass it.

**Schema Structure:**

* `description` (string): Flavor text for logs and UI.

* `mods` (array of objects): Standard engine modifiers using `"expr"`. Applies passively to the entity blueprint.

* `payload_immunities` (array of strings): Hazard IDs bypassed.

* `grants_skills` (array of strings): Passive or active Skill IDs bestowed.

**Example Entry:**

"Fly": {
  "description": "True aerodynamic flight requiring forward momentum.",
  "mods": [
    { "target": "evasion", "op": "add", "expr": "2" }
  ],
  "payload_immunities": ["Trip_And_Fall", "Lava_Burn", "Ground_Tremors"],
  "grants_skills": []
}


## 6. Vision Types (`Definitions/types_and_ranges/vision_types.json`)

**Purpose:** Defines biological and magical ocular capabilities. It dictates how an entity parses light and perceives threats, countering specific visual impairments cast by weather or terrain.

**Engine Implementation Notes:**

* **Bitmask Architecture:** Parsed as `uint64_t visionFlags`. A value of `0` strictly implies "Blind" (unable to process visual data). `Standard_Vision` is mapped to the first bit (`1 << 0`).

* **Hazard Mitigation:** Works identically to Traversal immunities. A blizzard casting "Blizzard_Blindness" will be nullified if the entity's vision flags (like `Thermal_Vision`) contain that immunity.

**Schema Structure:**

* `description` (string): Flavor text for logs and UI.

* `mods` (array of objects): Standard engine modifiers using `"expr"`. Used to dynamically scale the entity's base `vision_range` stat.

* `payload_immunities` (array of strings): Visual impairments and illusions ignored by this vision type.

* `grants_skills` (array of strings): Skill IDs granted (e.g., Telescopic Vision granting "Keen Sight").

**Example Entry:**

"Thermal_Vision": {
  "description": "Detection of infrared heat signatures.",
  "mods": [],
  "payload_immunities": ["Optical_Invisibility", "Smoke_Blindness", "Pitch_Black_Blindness", "Blizzard_Blindness"],
  "grants_skills": ["Heat Vision"]
}


## 7. Hearing Types (`Definitions/types_and_ranges/hearing_types.json`)

**Purpose:** Defines auditory perception capabilities. It determines how an entity interacts with sound waves, vibrations, and acoustic stealth mechanics.

**Engine Implementation Notes:**

* **Bitmask Architecture:** Parsed as `uint64_t hearingFlags`. A value of `0` strictly implies "Deaf". `Standard_Hearing` is mapped to the first bit (`1 << 0`).

* **Range Multipliers:** Many of these types utilize the `mods` array to heavily multiply the base `hearing_range` stat of the entity.

**Schema Structure:**

* `description` (string): Flavor text for logs and UI.

* `mods` (array of objects): Standard engine modifiers using `"expr"`. Used to dynamically scale the entity's base `hearing_range` stat.

* `payload_immunities` (array of strings): Auditory impairments or illusions ignored by this hearing type.

* `grants_skills` (array of strings): Skill IDs granted (e.g., Tremorsense granting "Tremor Sense").

**Example Entry:**

"Echolocation": {
  "description": "Active emission of sound waves to map surroundings.",
  "mods": [],
  "payload_immunities": ["Pitch_Black_Blindness", "Smoke_Blindness"],
  "grants_skills": ["Echolocation Blast"]
}


## 8. Scent Types (`Definitions/types_and_ranges/scent_types.json`)

**Purpose:** Defines olfactory perception and specialized chemoreception. Crucial for tracking mechanics, detecting invisible entities, and interacting with pheromone systems.

**Engine Implementation Notes:**

* **Bitmask Architecture:** Parsed as `uint64_t scentFlags`. A value of `0` strictly implies "Anosmia" (Scentless/Unable to smell). `Standard_Scent` is mapped to the first bit (`1 << 0`).

**Schema Structure:**

* `description` (string): Flavor text for logs and UI.

* `mods` (array of objects): Standard engine modifiers using `"expr"`. Used to dynamically scale the entity's base `scent_range` stat.

* `payload_immunities` (array of strings): Odor-based impairments ignored by this sense (e.g., resisting Miasma or Putrid Stench).

* `grants_skills` (array of strings): Skill IDs granted (e.g., Acute Scent granting "Tracking").

**Example Entry:**

"Jacobson_Organ": {
  "description": "Vomeronasal organ that 'tastes' heavy moisture-borne chemical particles in the air.",
  "mods": [],
  "payload_immunities": ["Wind_Dispersal"],
  "grants_skills": ["Directional Tracking"]
}


## 9. Damage Types (`Definitions/types_and_ranges/damage_types.json`)

**Purpose:** Defines the physical, biological, elemental, and magical mediums through which an entity's health (HP) is reduced.

**Engine Implementation Notes:**

* **Resistance Resolution:** The engine checks incoming damage flags against the defender's specific resistance stats (e.g., `fire_resist`) to calculate mitigation.

* **Payload Automation:** Automatically extracts the `payloads` array to cast them on the target (standardizing status effects).

**Schema Structure:**

* `description` (string): Flavor text and biological examples.

* `color` (string): Tailwind CSS color code for floating combat text.

* `payloads` (array of objects): Status effects triggered by suffering this damage type.

  * `{ "id": "Payload_Name", "chance_per_tick": float }`

**Example Entry:**

"Shredding": {
  "description": "Frantic surface-level tearing and flaying of skin/scales.",
  "color": "text-red-600",
  "payloads": [
    { "id": "Minor_Laceration", "chance_per_tick": 0.40 }
  ]
}


## 10. Skill Types (`Definitions/types_and_ranges/skill_types.json`)

**Purpose:** A comprehensive taxonomy of actions and traits an entity can possess, dictating how the engine applies global combat rules and allowing Status Effects to selectively disable capabilities.

**Engine Implementation Notes:**

* **Bitmask Architecture:** Parsed as `uint64_t skillTypeFlags`. These define the taxonomic nature of a skill.

* **Status Effect Disablement:** When an entity attempts to cast an active skill, the engine checks active Status Effects. If an active status possesses a `blocks_skill_types` array containing any flag matching the skill, the cast is prevented.

* **Combat Engine Events:** The `combat_flags` array generates standardized engine events (e.g., broadcasting an event to strip camouflage).

**Schema Structure:**

* `description` (string): Flavor text.

* `combat_flags` (array of strings): Engine-level event tags (e.g., "Breaks_Stealth").

**Example Entry:**

"Vocal": {
  "description": "Roars, howls, speech, or sonic bursts. Highly audible.",
  "combat_flags": ["Breaks_Stealth"]
}


## 11. Combat Tags (`Definitions/types_and_ranges/combat_tags.json`)

**Purpose:** Explicitly defines the "Magic Strings" used in `skill_types.json` and `skills.json` to inform the C++ systems of system logic.

**Engine Implementation Notes:**

* **No Attached Logic:** These entries contain no embedded mathematical logic or formulas. They act purely as a registry to bind human-readable UI text to the engine-level Hashes checked natively by C++ systems (like `StealthSystem` or `ReactionSystem`).

**Schema Structure:**

* `name` (string): The display name for the UI.

* `description` (string): The tooltip text explaining the mechanical rule to the player.

**Example Entry:**

"Breaks_Stealth": {
  "name": "Loud / Obvious",
  "description": "Executing this action instantly removes any active camouflage or stealth statuses."
}


## 12. Skills Registry (`GameData/skills.json`)

**Purpose:** The master database of every executable action or innate passive trait an entity can possess.

**Engine Implementation Notes:**

* **Passives:** If `types` includes "Passive", the engine evaluates the `mods` and `payloads` permanently upon entity initialization.

* **Damage Types Integration:** If a `mod` targets "hp", it must include a `damage_type`.

**Schema Structure:**

* `description` (string): UI tooltip.

* `types` (array of strings): Must match keys from `skill_types.json`.

* `range` (string/int): "Melee", "Audible", or a numerical grid value.

* `mods` (array of objects): Strict mathematical operations.

  * `{ "target": string, "op": string, "expr": string, "damage_type": string (optional) }`

* `payloads` (array of objects): Status effects or hazards cast upon execution.

  * `{ "id": "Status_ID", "chance_per_tick": float, "duration_ticks": int }`

**Example Entry:**

"Bite": {
  "description": "Delivers a venomous bite.",
  "types": ["Melee_Attack", "Natural_Weapon", "Secretion"],
  "range": "Melee",
  "mods": [
    { "target": "hp", "op": "subtract", "expr": "1d6 + 2", "damage_type": "Piercing" }
  ],
  "payloads": [
    { "id": "Venomous_Bite", "chance_per_tick": 0.25, "duration_ticks": 10 }
  ]
}


## 13. Status Effects (`GameData/Mechanics/status_effects.json`)

**Purpose:** Defines temporary or ambient mechanical states applied to entities via Payloads (from environment, weather, or skills). The core mechanism of the Payload Architecture.

**Engine Implementation Notes:**

* **Skill Blocking:** The `blocks_skill_types` array checks against the `types` array of the entity's skills. If a match is found, the skill is disabled.

* **Dynamic Math:** Status effects use the full expression parser and can define dynamic mathematical logic via `stat_dependencies`.

**Schema Structure:**

* `description` (string): UI tooltip.

* `blocks_skill_types` (array of strings): Matches keys in `skill_types.json`.

* `mods` (array of objects): Mathematical adjustments applied while the status is active.

  * `{ "target": string, "op": string, "expr": string, "damage_type": string (optional), "stat_dependencies": array of strings }`

**Example Entry:**

"Ambient_Extreme_Heat": {
  "description": "Lethal heat rapidly drains hydration and heavily impairs recovery.",
  "blocks_skill_types": [],
  "mods": [
    {
      "target": "stamina_regen",
      "op": "multiply",
      "expr": "0.5",
      "stat_dependencies": []
    },
    {
      "target": "water_retention",
      "op": "subtract",
      "expr": "2",
      "stat_dependencies": []
    }
  ]
}


## 14. Base Stats (`GameData/Definitions/base_stats.json`)

**Purpose:** Defines the fundamental, irreducible attributes of an entity. These are the raw input values before any formula evaluation occurs.

**Engine Implementation Notes:**

* Handled internally as `StatType: Raw`. Modifying these directly alters the base core of the entity permanently.

**Schema Structure:**

* `displayName` (string): Human-readable UI name.

* `description` (string): Flavor text for UI tooltips.

* `baseValue` (float): The default baseline if unassigned by components.

* `spriteIcon` (string): Relative path to icon assets.

**Example Entry:**

"str": {
  "displayName": "Strength",
  "description": "Raw physical power and muscle mass.",
  "baseValue": 10.0,
  "spriteIcon": "icons/stats/str.png"
}


## 15. Derived Stats (`GameData/Definitions/derived_stats.json`)

**Purpose:** Defines the dynamic potentials and calculated pools (like HP, AC, Speed) resulting from the formulas scaling off Base Stats.

**Engine Implementation Notes:**

* Handled internally as `StatType: Potential`. The engine runs the `calculationFormula` string through the mathematical parser anytime an underlying dependency changes.

**Schema Structure:**

* `displayName` (string): Human-readable UI name.

* `description` (string): Flavor text for UI tooltips.

* `calculationFormula` (string): Executable formula parsed by the engine (e.g., `"(size_index * 2) * con"`).

* `spriteIcon` (string): Relative path to icon assets.

**Example Entry:**

"hp_max": {
  "displayName": "Max Health",
  "description": "The absolute limit of biological damage the entity can sustain before death.",
  "calculationFormula": "(size_index * 2) * con",
  "spriteIcon": "icons/stats/hp.png"
}