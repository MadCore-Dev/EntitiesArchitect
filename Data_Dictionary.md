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

> **📊 SYSTEM REGISTRY TRACKER (Auto-Extracted)**
> Use this list to verify that all referenced data points exist in `skills.json`, `status_effects.json`, and the Core Engine Stat definitions.
>
> ### 1. Skills Registry (Granted & Mutated)
> * **Movement/Agility:** Acrobatics, Burrow, Climb, Dart, Leap, Sprint, Squeeze, Sure-Footed, Swim, Wall Climb
> * **Combat/Tactics:** Ambush, Blood Frenzy, Constrict, Pack Tactics, Reaction Strike, Stealth, Venomous Bite
> * **Senses/Tracking:** Directional Tracking, Echolocation, Echolocation Blast, Heat Vision, Keen Sight, Tracking, Tremor Sense
> * **Biological Passives:** Amphibious, Camouflage, Cold Blooded, Disease Immunity, Endurance, Fire Resistance, Forage, Gills, Hibernate, Hive Mind, Incorporeal, Magic Resistance, Necrotic Resistance, Obsidian Skin, Poison Resistance, Psionic, Reflective Carapace, Scavenger, Thermal Vision, Thick Fur, Undead Nature, Water Retention
>
> ### 2. Payloads & Immunities (Hazards, Statuses, Traps)
> * **Environmental Hazards:** Arcane_Lightning, Ash_Inhalation, Cave_In, Choking_Dust, Crushing_Pressure, Current_Drag, Drowning, Extreme_Burn, Fall_Damage, Freezing_Wind, Frostbite, Ground_Tremors, Heatstroke, Hypoxia, Jungle_Fever, Lava_Burn, Lava_Fissure, Mana_Burn, Miasma_Poison, Minor_Laceration, Overheating, Physical_Traps, Plummet, Soul_Drain, Suffocation, Surface_Hazards, Swept_Away, Trip_And_Fall
> * **Sensory Impairments (Auras):** Ambient_Noise, Arcane_Interference, Ash_Blindness, Auditory_Illusions, Blizzard_Blindness, Blur_Distortion, Dazzle, Dense_Canopy_Obscurity, Dim_Light_Penalty, High_Vantage_Aura, Magical_Fog_Obscurity, Magical_Illusion, Mirage, Optical_Camouflage, Optical_Invisibility, Pitch_Black_Blindness, Putrid_Stench, Rain_Obscurity, Refractive_Glare, Sandstorm_Blind, Shapechanger_Deceit, Smoke_Blindness, Snowblindness, Stagnant_Air, Storm_Deafness, Underwater_Blur, Underwater_Muffling, Ventriloquism, Wind_Dispersal
> * **Combat Statuses & Damage Procs:** Bleeding, Blinded, Charm, Concussion, Confusion, Corroded, Deep_Wound, Deafened, Flanking_Advantage, Frostbite, Grappled, Ignite, Infected, Knocked_Prone, Paralyzed, Poisoned, Prone, Restrained, Web_Ensnare, Web_Vibration, Withering
> * **Combat Engine Event Flags:** Breaks_Stealth, Provokes_Reaction
> 
> ### 3. Mod Targets (Engine Stats Registry)
> * **Core Stats:** `con`, `dex`, `int`, `str`, `wis`
> * **Derived Combat:** `evasion`, `natural_armor`, `speed_bonus`
> * **Senses:** `hearing_range`, `scent_range`, `sense_bonus`, `vision_range`
> * **Resources:** `stamina`, `stamina_regen`, `water_retention`

---

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
```json
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
```

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

**Purpose:** Defines the dynamic, shifting meteorological events that overlay on top of a Biome's base state. Weather can dramatically alter combat via sensory impairments (cast as constant Payloads) and can actively mutate the physical map by adding temporary terrain properties.

**Engine Implementation Notes:**
* **Dynamic Map Mutation:** When weather changes, the engine must read `terrain_additions` and temporarily append those tags to exposed tiles in the chunk (e.g., "Raining" dynamically adds the "Mud" tag to Dirt tiles).
* **Sensory Overrides & Hazards:** The `payloads` array handles both immediate, volatile hazards (like Lightning Strikes) and persistent sensory debuffs (like Blizzard Blindness). Sensory debuffs should be configured with `"chance_per_tick": 1.0`.

**Schema Structure:**
* `description` (string): Flavor text for logs and UI.
* `terrain_additions` (array of strings): Matches keys from `terrain_types.json`. Applied temporarily to the chunk's tiles while the weather is active.
* `payloads` (array of objects): Standard environment hazard payloads and sensory auras.
  * `{ "id": "Payload_Name", "chance_per_tick": float }`

**Example Entry:**
```json
"Blizzard": {
  "description": "A blinding storm of snow and ice.",
  "terrain_additions": ["Ice", "Slippery"],
  "payloads": [
    { "id": "Freezing_Wind", "chance_per_tick": 0.05 },
    { "id": "Blizzard_Blindness", "chance_per_tick": 1.0 },
    { "id": "Storm_Deafness", "chance_per_tick": 1.0 }
  ]
}

```

---

## 5. Traversal Types (`Definitions/types_and_ranges/traversal_types.json`)

**Purpose:** Defines the physical or magical methods an entity uses to navigate the game world. This serves as a primary biological blueprint for how creatures interact with complex terrain and environmental physics.

**Engine Implementation Notes:**
* **Bitmask Architecture:** The engine parses these keys into a `uint64_t traversalFlags` bitmask. An entity can possess multiple flags simultaneously. A value of `0` strictly implies "Immobile." `Walk` should be mapped to the first bit (`1 << 0`).
* **Terrain Interlocking:** When an entity enters a terrain tile with a `required_traversal`, the engine must do a bitwise `AND` check against the entity's flags.
* **Physics Automation:** If an environmental payload (e.g., "Trip_And_Fall" from slippery ice) attempts to cast on the entity, the engine checks the `payload_immunities` array of their active traversal flags. If a match is found, the cast is aborted.

**Schema Structure:**
* `description` (string): Flavor text for logs and UI.
* `mods` (array of objects): Standard engine modifiers using `"expr"`. Applies passively to the entity (e.g., increasing base speed or evasion).
* `payload_immunities` (array of strings): A list of environmental hazard IDs or status payloads that this form of movement naturally bypasses.
* `grants_skills` (array of strings): A list of passive or active Skill IDs automatically bestowed upon the entity (e.g., Brachiation granting Acrobatics).

**Example Entry:**
```json
"Fly": {
  "description": "True aerodynamic flight requiring forward momentum.",
  "mods": [
    { "target": "evasion", "op": "add", "expr": "2" }
  ],
  "payload_immunities": ["Trip_And_Fall", "Lava_Burn", "Ground_Tremors"],
  "grants_skills": []
}

```

---

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

```json
"Thermal_Vision": {
  "description": "Detection of infrared heat signatures.",
  "mods": [],
  "payload_immunities": ["Optical_Invisibility", "Smoke_Blindness", "Pitch_Black_Blindness", "Blizzard_Blindness"],
  "grants_skills": ["Heat Vision"]
}

```

---

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

```json
"Echolocation": {
  "description": "Active emission of sound waves to map surroundings.",
  "mods": [],
  "payload_immunities": ["Pitch_Black_Blindness", "Smoke_Blindness"],
  "grants_skills": ["Echolocation Blast"]
}

```

---

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

```json
"Jacobson_Organ": {
  "description": "Vomeronasal organ that 'tastes' heavy moisture-borne chemical particles in the air.",
  "mods": [],
  "payload_immunities": ["Wind_Dispersal"],
  "grants_skills": ["Directional Tracking"]
}

```

---

## 9. Damage Types (`Definitions/types_and_ranges/damage_types.json`)

**Purpose:** Defines the physical, biological, elemental, and magical mediums through which an entity's health (HP) is reduced. Covers everything from biological natural weapons to esoteric magic.

**Engine Implementation Notes:**
* **Bitmask Architecture:** Parsed as `uint64_t damageFlags`. An attack can deal multiple types of damage simultaneously (e.g., a toxic bite is `Piercing | Poison`).
* **Resistance Resolution:** When an entity takes damage, the engine checks the incoming damage flags against the defender's specific resistance stats (e.g., `fire_resist`, `slashing_resist`) to calculate mitigation.
* **Payload Automation:** When an attack deals a specific damage type, the engine automatically extracts the `payloads` array from this file and attempts to cast them on the target. This standardizes status effects without hardcoding them into every individual skill.

**Schema Structure:**
* `description` (string): Flavor text and biological examples.
* `color` (string): Tailwind CSS color code used for floating combat text and UI rendering.
* `payloads` (array of objects): Standard engine payloads triggered by suffering this damage type.
  * `{ "id": "Payload_Name", "chance_per_tick": float }`

**Example Entry:**
```json
"Shredding": {
  "description": "Frantic surface-level tearing and flaying of skin/scales.",
  "color": "text-red-600",
  "payloads": [
    { "id": "Minor_Laceration", "chance_per_tick": 0.40 }
  ]
}
```

---

## 10. Skill Types (`Definitions/types_and_ranges/skill_types.json`)

**Purpose:** A comprehensive taxonomy of actions and traits an entity can possess. These tags categorize the nature of a skill, dictating how the engine applies global combat rules and allowing Status Effects to selectively disable specific capabilities.

**Engine Implementation Notes:**
* **Bitmask Architecture:** Parsed as `uint64_t skillTypeFlags`. A skill can possess multiple types (e.g., a toxic bite is `Melee_Attack | Natural_Weapon | Secretion`).
* **Passive Evaluation:** If a skill possesses the `Passive` flag, the engine automatically extracts its `mods` and `payloads` and applies them permanently to the entity during initialization. The skill cannot be actively cast.
* **Status Effect Disablement:** When an entity attempts to cast an active skill, the engine checks active Status Effects. If an active status possesses a `"blocks_skill_types"` array containing any flag matching the skill, the cast is prevented.
* **Combat Engine Events:** The `combat_flags` array generates standardized engine events. If an entity uses a skill with the `Breaks_Stealth` tag, the engine broadcasts an event to strip their camouflage.

**Schema Structure:**
* `description` (string): Flavor text defining the category.
* `combat_flags` (array of strings): Engine-level event tags (e.g., "Breaks_Stealth", "Provokes_Reaction") triggered automatically when the skill is executed.

**Example Entry:**
```json
"Vocal": {
  "description": "Roars, howls, speech, or sonic bursts. Highly audible.",
  "combat_flags": ["Breaks_Stealth"]
}
```

---

## 11. Combat Tags (`Definitions/types_and_ranges/combat_tags.json`)

**Purpose:** The master dictionary for engine-level execution tags. This explicitly defines the "Magic Strings" used in `skill_types.json` and `skills.json`, allowing the engine to assign them system Hashes/Bitmasks at startup and providing the UI with tooltip descriptions.

**Engine Implementation Notes:**
* **No Attached Logic:** These entries contain no logic or hooks. They exist purely to register the existence of the tag into the engine's memory. The C++ systems (like `StealthSystem` or `ReactionSystem`) check for the presence of these hashes to run their native logic.

**Schema Structure:**
* `name` (string): The display name for the UI.
* `description` (string): The tooltip text explaining the mechanical rule to the player.

**Example Entry:**
```json
"Breaks_Stealth": {
  "name": "Loud / Obvious",
  "description": "Executing this action instantly removes any active camouflage or stealth statuses."
}
```

---

