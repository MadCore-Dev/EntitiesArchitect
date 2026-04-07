# EntitiesArchitect — MadCore RPG: Full Project Overview

> **Purpose of this document:** A comprehensive snapshot of the `EntitiesArchitect` project — its architecture, all data types, their schemas, and exact entry counts. Intended to be read alongside `skills.json` and `status_effects.json` by an AI assistant for further design expansion.

---

## Table of Contents

1. [Project Architecture](#1-project-architecture)
2. [Directory Map](#2-directory-map)
3. [Lineages (Creature Types)](#3-lineages-creature-types)
4. [Entity Part System — Structure](#4-entity-part-system--structure)
5. [Entity Part Counts by Lineage](#5-entity-part-counts-by-lineage)
6. [Core Definitions](#6-core-definitions--type-registries)
7. [Mechanics Files](#7-mechanics-files)
8. [World Data](#8-world-data)
9. [Skills & Status Effects Summary](#9-skills--status-effects-summary)
10. [Global Data Summary Table](#10-global-data-summary-table)

---

## 1. Project Architecture

**MadCore RPG** is a data-driven procedural creature generation system. Entities (creatures) are built at runtime by assembling JSON component files from a library organized by **Lineage** (creature archetype). The engine applies math formulas defined in Definitions to calculate final stats from the aggregated component modifiers.

### Core Principles

| Principle | Description |
|---|---|
| **Everything is a Payload** | Continuous buffs/debuffs are never naked mods. They are Status Effects cast by Skills or environment at `chance_per_tick`. |
| **Procedural Slot Assembly** | A `chassis.json` entry defines `slots` (e.g., `leg_fore_left`, `maw_primary`). The generator fills each slot from the relevant lineage-specific JSON file. |
| **Bitmask Flags** | Traversal, Vision, Hearing, Scent types are parsed into `uint64_t` bitmasks for O(1) lookups. |
| **Expression Parser** | All `mods` use an `"expr"` string (e.g. `"2d4 + con"`) parsed at runtime. `stat_dependencies` flags which base stats the expression reads. |
| **Lineage Tiers** | Natural lineages have 10 entries per part; Exotic/Special lineages have 12 entries per part. |

---

## 2. Directory Map

```
EntitiesArchitect/
├── GameData/
│   ├── skills.json                    ← Master skill database (217 entries)
│   ├── prefixes.json                  ← Entity name prefixes (7 entries)
│   ├── consumable_categories.json     ← Harvestable food types (8 entries)
│   │
│   ├── Definitions/
│   │   ├── base_stats.json            ← Raw input stats (15 entries)
│   │   ├── derived_stats.json         ← Formula-based stats (37 entries)
│   │   ├── combat_tags.json           ← Engine event registry (6 entries)
│   │   ├── operations.json            ← Math operations (5 entries)
│   │   ├── validation_rules.json      ← Schema validation
│   │   └── types_and_ranges/
│   │       ├── damage_types.json      (16 entries)
│   │       ├── terrain_types.json     (31 entries)
│   │       ├── skill_types.json       (20 entries)
│   │       ├── traversal_types.json   (22 entries)
│   │       ├── vision_types.json      (12 entries)
│   │       ├── hearing_types.json     (8 entries)
│   │       └── scent_types.json       (6 entries)
│   │
│   ├── Mechanics/
│   │   ├── status_effects.json        ← Status effect database (93 entries)
│   │   ├── behaviors.json             ← AI combat behaviors (4 entries)
│   │   ├── anatomy_drops.json         ← Harvesting drop slots (26 entries)
│   │   ├── harvest_types.json         ← Harvest action definitions (9 entries)
│   │   ├── biological_upgrades.json   ← Upgrade paths (8 entries)
│   │   ├── loot_quality.json          ← Quality tiers (16 entries)
│   │   ├── leveling_rules.json        ← Level scaling rules
│   │   └── growth_stages/
│   │       ├── size_indices.json      ← Size: Tiny→Colossal (6 sizes)
│   │       └── stages.json            ← Growth stage definitions
│   │
│   ├── World/
│   │   ├── biomes.json                (13 entries)
│   │   ├── temperature_bands.json     (8 entries)
│   │   ├── weather_types.json         (11 entries)
│   │   └── spawning_rules/
│   │       ├── group_scaling.json     (6 entries)
│   │       └── size_limits.json       (6 entries)
│   │
│   └── Entities/
│       ├── Appendages/
│       │   ├── arms/        (31 lineage files + common.json)
│       │   ├── fins/        (32 lineage files + common.json)
│       │   ├── legs/        (31 lineage files + common.json)
│       │   ├── tails/       (32 lineage files + common.json)
│       │   ├── tentacles/   (32 lineage files + common.json)
│       │   └── wings/       (32 lineage files + common.json)
│       ├── Cephalon/
│       │   ├── cranium/     (32 lineage files + common.json)
│       │   ├── ears/        (32 lineage files + common.json)
│       │   ├── eyes/        (32 lineage files + common.json)
│       │   ├── maw/         (31 lineage files + common.json)
│       │   └── nose/        (32 lineage files + common.json)
│       ├── Core/
│       │   ├── chassis/     (32 lineage files + common.json)
│       │   ├── integument/  (32 lineage files + common.json)
│       │   └── appearance/
│       │       ├── patterns.json      (7 entries — universal)
│       │       └── pigmentation.json  (7 entries — universal)
│       ├── Flora/           [STUB — not yet implemented]
│       │   ├── canopy/      (common.json only)
│       │   └── roots/       (common.json only)
│       └── Geological/      [STUB — not yet implemented]
│           ├── composition/ (common.json only)
│           └── formation/   (common.json only)
│
├── Data_Dictionary.md       ← Schema documentation (reference doc)
├── MadCoreRPG_Architecture.md
├── madcore.schema.json      ← Formal JSON schema
├── gamedata.db              ← SQLite cache of generated entities
└── index.html               ← UI viewer / editor
```

---

## 3. Lineages (Creature Types)

There are **32 distinct lineages** organized into two tiers. Each lineage has its own file in every entity part directory.

### Tier 1 — Natural (10 entries per part)
Standard organic creature archetypes.

| Lineage | Description |
|---|---|
| `amphibian` | Frogs, salamanders, toads |
| `arachnid` | Spiders, scorpions, web-spinners |
| `avian` | Birds, raptors, large flightless |
| `canine` | Dogs, wolves, foxes |
| `construct` | Animated golems, mechanical beings |
| `feline` | Cats, lions, big cats |
| `fungal` | Mushroom-entities, mycelial creatures |
| `hyenid` | Hyenas, spotted predators |
| `insect` | Beetles, moths, swarm insects |
| `marsupial` | Kangaroos, wombats, quolls |
| `mustelid` | Ferrets, badgers, wolverines |
| `pholidota` | Pangolins, scaled crawlers |
| `piscine` | Fish, eels, aquatic vertebrates |
| `plant` | Mobile plant-based organisms |
| `primate` | Apes, monkeys, simians |
| `rodent` | Rats, beavers, giant rodents |
| `saurian` | Lizards, crocodiles, monitor types |
| `ungulate` | Deer, bison, hoofed mammals |
| `ursine` | Bears, pandas, large ursids |
| `vermian` | Worms, centipedes, serpentine crawlers |

### Tier 2 — Exotic / Special (12 entries per part)
Supernatural, magical, or extreme morphology archetypes.

| Lineage | Description |
|---|---|
| `aberrant` | Eldritch, non-euclidean bio-horrors |
| `celestial` | Divine or cosmic origin creatures |
| `cephalopod` | Octopi, squids, nautiloid types |
| `chiropteran` | Bats, shadow-winged predators |
| `crustacean` | Crabs, lobsters, armored arthropods |
| `demonkin` | Infernal, corrupted demon-blooded |
| `draconic` | Dragon-kin, wyrms, scale lords |
| `elemental` | Pure elemental matter-beings |
| `elephantine` | Elephants, mastodons, megafauna |
| `fae` | Fey creatures, nature spirits |
| `marsupial` | *(12 entries, exotic variants)* |
| `mustelid` | *(12 entries, exotic variants)* |
| `ooze` | Slimes, puddings, amorphous predators |
| `rodent` | *(12 entries, exotic variants)* |
| `spectral` | Ghosts, wraiths, incorporeal entities |

> **Note:** Some lineages appear in both tiers depending on whether they appear in natural (10) or exotic (12) file categories. The count difference is per-part-directory.

---

## 4. Entity Part System — Structure

Each creature entity is assembled from **15 component slots** (defined by the chassis). Below is the schema for each component type.

### 4.1 Core/chassis — The Body Frame

**Path:** `GameData/Entities/Core/chassis/<lineage>.json`

```json
"<ChassisName>": {
  "tags":          ["string"],      // Taxonomic/structural labels
  "meat_group":    ["string"],      // Harvesting categories (see consumable_categories.json)
  "slots": {                        // Key = slot name, Value = directory path to sample from
    "head":           "Cephalon/cranium",
    "integument":     "Core/integument",
    "pattern_layer":  "Core/appearance",
    "pigment_layer":  "Core/appearance",
    "leg_fore_left":  "Appendages/legs",
    "leg_fore_right": "Appendages/legs",
    "leg_rear_left":  "Appendages/legs",
    "leg_rear_right": "Appendages/legs",
    "tail_main":      "Appendages/tails"
    // ...varies by body plan
  },
  "mods":          [ModObject],     // Foundational base stat adjustments
  "grants_skills": ["string"],      // Innate passive skills
  "description":   "string"
}
```

### 4.2 Core/integument — Outer Skin Layer

**Path:** `GameData/Entities/Core/integument/<lineage>.json`

```json
"<IntegumentName>": {
  "tags":          ["string"],   // Skin type labels (Scales, Chitin, Slime, etc.)
  "mods":          [ModObject],  // Resist/stat bonuses
  "grants_skills": ["string"],   // Camouflage, Poison_Cloud, etc.
  "description":   "string"
}
```

### 4.3 Core/appearance — Visual Layer (Universal)

**Path:** `GameData/Entities/Core/appearance/patterns.json` and `pigmentation.json`

These are **single shared files** (not per-lineage). All entities draw from the same pool.

```json
// patterns.json entry:
"<PatternName>": {
  "mods":           [ModObject],   // Usually minor dex/cha tweaks
  "biome_affinity": ["string"],    // Biomes where this pattern grants stealth
  "description":    "string"
}

// pigmentation.json entry:
"<PigmentName>": {
  "flavor":      "string",         // Short thematic note
  "mods":        [ModObject],
  "description": "string"
}
```

**Patterns (7):** `None`, `Mottled`, `Striped`, `Spotted`, `Brindled`, `Rosette`, `Reticulated`

**Pigmentations (7):** `Standard`, `Melanistic`, `Albino`, `Leucistic`, `Erythristic`, `Xanthic`, `Iridescent`

### 4.4 Cephalon/cranium — The Head Frame

**Path:** `GameData/Entities/Cephalon/cranium/<lineage>.json`

```json
"<CraniumName>": {
  "tags":    ["string"],
  "slots": {                          // Defines sub-slots on the head
    "eye_left":    "Cephalon/eyes",
    "eye_right":   "Cephalon/eyes",
    "ear_left":    "Cephalon/ears",
    "ear_right":   "Cephalon/ears",
    "maw_primary": "Cephalon/maw",
    "nose_primary":"Cephalon/nose"
  },
  "mods":          [ModObject],
  "grants_skills": ["string"],
  "description":   "string"
}
```

### 4.5 Cephalon/ears, eyes, maw, nose — Sensory Organs

**Path:** `GameData/Entities/Cephalon/<organ>/<lineage>.json`

All four share the same base schema:

```json
"<OrganName>": {
  "tags":          ["string"],   // Type labels
  "mods":          [ModObject],  // Perception, initiative, attack bonuses
  "grants_skills": ["string"],   // e.g., "Keen Sight", "Tremorsense", "Bite"
  "description":   "string"
}
```

### 4.6 Appendages — Limbs & Locomotion

**Path:** `GameData/Entities/Appendages/<type>/<lineage>.json`

All 6 appendage types (arms, fins, legs, tails, tentacles, wings) share:

```json
"<AppendageName>": {
  "tags":          ["string"],       // Limb type labels
  "traversal":     ["string"],       // Flags from traversal_types.json
  "mods":          [ModObject],      // str, dex, reach, jump_distance, etc.
  "grants_skills": ["string"],       // Grapple, Aerobatics, etc.
  "description":   "string"
}
```

### 4.7 The ModObject — Universal Modifier

Used in every component type:

```json
{
  "target":            "string",   // Stat key (e.g., "hp", "str", "poison_resist")
  "op":                "string",   // "add" | "subtract" | "multiply" | "divide" | "set"
  "expr":              "string",   // Math expression e.g., "2d4 + con", "0.5"
  "damage_type":       "string",   // Only for "target":"hp" entries
  "stat_dependencies": ["string"]  // Stats the expr reads at runtime
}
```

---

## 5. Entity Part Counts by Lineage

Each cell shows the number of named entries in that lineage's file for that part.
`—` = file is a stub (empty `{}`) or not present. `[U]` = universal (single shared file).

### 5.1 Core Parts

| Lineage | chassis | integument | patterns | pigmentation |
|---|---|---|---|---|
| aberrant | 12 | 12 | [U] 7 | [U] 7 |
| amphibian | 10 | 10 | [U] 7 | [U] 7 |
| arachnid | 10 | 10 | [U] 7 | [U] 7 |
| avian | 10 | 10 | [U] 7 | [U] 7 |
| canine | 10 | 10 | [U] 7 | [U] 7 |
| celestial | 12 | 12 | [U] 7 | [U] 7 |
| cephalopod | 12 | 12 | [U] 7 | [U] 7 |
| chiropteran | 12 | 12 | [U] 7 | [U] 7 |
| construct | 10 | 10 | [U] 7 | [U] 7 |
| crustacean | 12 | 12 | [U] 7 | [U] 7 |
| demonkin | 12 | 12 | [U] 7 | [U] 7 |
| draconic | 12 | 12 | [U] 7 | [U] 7 |
| elemental | 12 | 12 | [U] 7 | [U] 7 |
| elephantine | 12 | 12 | [U] 7 | [U] 7 |
| fae | 12 | 12 | [U] 7 | [U] 7 |
| feline | 10 | 10 | [U] 7 | [U] 7 |
| fungal | 10 | 10 | [U] 7 | [U] 7 |
| hyenid | 12 | 12 | [U] 7 | [U] 7 |
| insect | 10 | 10 | [U] 7 | [U] 7 |
| marsupial | 12 | 12 | [U] 7 | [U] 7 |
| mustelid | 12 | 12 | [U] 7 | [U] 7 |
| ooze | 12 | 12 | [U] 7 | [U] 7 |
| pholidota | 12 | 12 | [U] 7 | [U] 7 |
| piscine | 10 | 10 | [U] 7 | [U] 7 |
| plant | 10 | 10 | [U] 7 | [U] 7 |
| primate | 10 | 10 | [U] 7 | [U] 7 |
| rodent | 12 | 12 | [U] 7 | [U] 7 |
| saurian | 10 | 10 | [U] 7 | [U] 7 |
| spectral | 12 | 12 | [U] 7 | [U] 7 |
| ungulate | 10 | 10 | [U] 7 | [U] 7 |
| ursine | 10 | 10 | [U] 7 | [U] 7 |
| vermian | 12 | 12 | [U] 7 | [U] 7 |

### 5.2 Cephalon Parts

| Lineage | cranium | ears | eyes | maw | nose |
|---|---|---|---|---|---|
| aberrant | 12 | 12 | 12 | 12 | 12 |
| amphibian | 10 | 10 | 10 | 10 | 10 |
| arachnid | 10 | 10 | 10 | 10 | 10 |
| avian | 10 | 10 | 10 | 10 | 10 |
| canine | 10 | 10 | 10 | 10 | 10 |
| celestial | 12 | 12 | 12 | 12 | 12 |
| cephalopod | 12 | 12 | 12 | 12 | 12 |
| chiropteran | 12 | 12 | 12 | 12 | 12 |
| construct | 10 | 10 | 10 | 10 | 10 |
| crustacean | 12 | 12 | 12 | 12 | 12 |
| demonkin | 12 | 12 | 12 | 12 | 12 |
| draconic | 12 | 12 | 12 | 12 | 12 |
| elemental | 12 | 12 | 12 | 12 | 12 |
| elephantine | 12 | 12 | 12 | 12 | 12 |
| fae | 12 | 12 | 12 | — | 12 |
| feline | 10 | 10 | 10 | 10 | 10 |
| fungal | 10 | 10 | 10 | 10 | 10 |
| hyenid | 12 | 12 | 12 | 12 | 12 |
| insect | 10 | 10 | 10 | 10 | 10 |
| marsupial | 12 | 12 | 12 | 12 | 12 |
| mustelid | 12 | 12 | 12 | 12 | 12 |
| ooze | 12 | 12 | 12 | 12 | 12 |
| pholidota | 12 | 12 | 12 | 12 | 12 |
| piscine | 10 | 10 | 10 | 10 | 10 |
| plant | 10 | 10 | 10 | 10 | 10 |
| primate | 10 | 10 | 10 | 10 | 10 |
| rodent | 12 | 12 | 12 | 12 | 12 |
| saurian | 10 | 10 | 10 | 10 | 10 |
| spectral | 12 | 12 | 12 | 12 | 12 |
| ungulate | 10 | 10 | 10 | 10 | 10 |
| ursine | 10 | 10 | 10 | 10 | 10 |
| vermian | 12 | 12 | 12 | 12 | 12 |

> **Note on `fae/maw`:** File not present in maw directory — `fae` appears to be queued for maw data.

### 5.3 Appendage Parts

| Lineage | arms | fins | legs | tails | tentacles | wings |
|---|---|---|---|---|---|---|
| aberrant | 12 | 12 | — | 12 | 12 | 12 |
| amphibian | 10 | 10 | 10 | 10 | 10 | 10 |
| arachnid | 10 | 10 | 10 | 10 | 10 | 10 |
| avian | 10 | 10 | 10 | 10 | 10 | 10 |
| canine | 10 | 10 | 10 | 10 | 10 | 10 |
| celestial | 12 | 12 | 12 | 12 | 12 | 12 |
| cephalopod | 12 | 12 | 12 | 12 | 12 | 12 |
| chiropteran | 12 | 12 | 12 | 12 | 12 | 12 |
| construct | 10 | 10 | 10 | 10 | 10 | 10 |
| crustacean | 12 | 12 | 12 | 12 | 12 | 12 |
| demonkin | 12 | 12 | 12 | 12 | 12 | 12 |
| draconic | 12 | 12 | 12 | 12 | 12 | 12 |
| elemental | 12 | 12 | 12 | 12 | 12 | 12 |
| elephantine | 12 | 12 | 12 | 12 | 12 | 12 |
| fae | — | 12 | 12 | 12 | 12 | 12 |
| feline | 10 | 10 | 10 | 10 | 10 | 10 |
| fungal | 10 | 10 | 10 | 10 | 10 | 10 |
| hyenid | 12 | 12 | 12 | 12 | 12 | 12 |
| insect | 10 | 10 | 10 | 10 | 10 | 10 |
| marsupial | 12 | 12 | 12 | 12 | 12 | 12 |
| mustelid | 12 | 12 | 12 | 12 | 12 | 12 |
| ooze | 12 | 12 | 12 | 12 | 12 | 12 |
| pholidota | 12 | 12 | 12 | 12 | 12 | 12 |
| piscine | 10 | 10 | 10 | 10 | 10 | 10 |
| plant | 10 | 10 | 10 | 10 | 10 | 10 |
| primate | 10 | 10 | 10 | 10 | 10 | 10 |
| rodent | 12 | 12 | 12 | 12 | 12 | 12 |
| saurian | 10 | 10 | 10 | 10 | 10 | 10 |
| spectral | 12 | 12 | 12 | 12 | 12 | 12 |
| ungulate | 10 | 10 | 10 | 10 | 10 | 10 |
| ursine | 10 | 10 | 10 | 10 | 10 | 10 |
| vermian | 12 | 12 | 12 | 12 | 12 | 12 |

> **Notes:** `aberrant/arms` and `aberrant/legs` + `fae/arms` show as `—` (missing or stub).

---

## 6. Core Definitions / Type Registries

### 6.1 Base Stats (`Definitions/base_stats.json`) — 15 entries

Fundamental entity attributes. `statType: "Raw"`.

| Stat Key | Display Name | Base Value |
|---|---|---|
| str | Strength | 10.0 |
| dex | Dexterity | 10.0 |
| con | Constitution | 10.0 |
| int | Intelligence | 10.0 |
| wis | Wisdom | 10.0 |
| cha | Charisma | 10.0 |
| size_index | Size Index | 4.0 |
| perception | Perception | 10.0 |
| vision_range | Vision Range | 10.0 |
| hearing_range | Hearing Range | 10.0 |
| scent_range | Scent Range | 10.0 |
| reach | Reach | 1.0 |
| jump_distance | Jump Distance | 1.0 |
| water_retention | Water Retention | 10.0 |
| stealth | Stealth | 0.0 |

### 6.2 Derived Stats (`Definitions/derived_stats.json`) — 37 entries

Calculated potentials. `statType: "Potential"`. Engine re-evaluates `calculationFormula` on dependency change.

Key examples:

| Stat Key | Formula | Description |
|---|---|---|
| hp_max | `(size_index * 2) * con` | Max health pool |
| stamina_max | `(dex + con) * 5` | Max stamina pool |
| natural_armor | `(size_index * 0.5) + con` | Base physical defense |
| speed | `dex * 2` | Movement units per tick |
| initiative | `dex + wis` | Combat reaction order |
| evasion | `dex + agility` | Dodge chance |
| jump_height | `str + jump_distance` | Vertical leap |
| stamina_regen | `con * 0.1` | Per-tick stamina recovery |

*(Full list of 37 stats available in `derived_stats.json`)*

### 6.3 Operations (`Definitions/operations.json`) — 5 entries

Valid math operations for the `"op"` field in ModObjects:

| Op | Description |
|---|---|
| `add` | Additive bonus |
| `subtract` | Deduction |
| `multiply` | Multiplicative scaling |
| `divide` | Division (rare) |
| `set` | Hard override |

### 6.4 Type Registries

#### Damage Types — 16 entries
`Piercing`, `Slashing`, `Bludgeoning`, `Shredding`, `Acid`, `Fire`, `Ice`, `Lightning`, `Poison`, `Necrotic`, `Radiant`, `Psychic`, `Sonic`, `Bleed`, `True`, `Arcane`

#### Terrain Types — 31 entries
Categories: `surface`, `topography`, `cover`, `condition`, `liquid`, `lighting`
Examples: `Grass`, `Rock`, `Sand`, `Aquatic`, `Magma`, `Ice`, `Dense_Foliage`, `Slippery`, `Steep`

#### Skill Types — 20 entries
Taxonomic tags for skill classification (used for bitmask-blocking by Status Effects).
Examples: `Melee_Attack`, `Ranged_Attack`, `Passive`, `Vocal`, `Natural_Weapon`, `Secretion`, `Locomotion`, `Defensive`, `Social`, `Aerial`

#### Traversal Types — 22 entries
Examples: `Walk`, `Run`, `Swim`, `Fly`, `Burrow`, `Climb`, `Leap`, `Glide`, `Slither`, `Phase`, `Hover`

#### Vision Types — 12 entries
Examples: `Standard_Vision`, `Thermal_Vision`, `Darkvision`, `Sonar_Vision`, `UV_Vision`, `Telescopic_Vision`, `Compound_Eye`, `Blindsight`

#### Hearing Types — 8 entries
Examples: `Standard_Hearing`, `Echolocation`, `Tremorsense`, `Acute_Hearing`, `Deafened`, `Infrasound`

#### Scent Types — 6 entries
Examples: `Standard_Scent`, `Acute_Scent`, `Jacobson_Organ`, `Chemoreception`, `Anosmia`, `Vomeronasal`

### 6.5 Combat Tags (`Definitions/combat_tags.json`) — 6 entries

Engine-level event strings bound to C++ system hashes. No math logic, purely semantic.

| Tag | Effect |
|---|---|
| `Breaks_Stealth` | Instantly removes active camouflage/stealth |
| *(5 more tags total)* | |

---

## 7. Mechanics Files

### 7.1 Status Effects (`Mechanics/status_effects.json`) — 93 entries

Temporary or ambient mechanical states applied via Payloads. See `status_effects.json` for full list.

**Schema:**
```json
"<StatusEffect_ID>": {
  "description":        "string",
  "blocks_skill_types": ["string"],   // Skill type keys blocked while active
  "mods":               [ModObject]   // Applied continuously while status is active
}
```

**Coverage includes:**
- Environmental (Heatstroke, Frostbite, Blizzard_Blindness)
- Damage-over-time (Acid_Burn, Bleed, Poison_Tick)
- Perception impairments (Smoke_Blindness, Storm_Deafness)
- Crowd control (Paralyzed, Stunned, Slowed)
- Buffs (Adrenaline_Rush, Camouflage)

### 7.2 Behaviors (`Mechanics/behaviors.json`) — 4 entries

AI combat archetypes assigned to entities.

| Behavior | Description |
|---|---|
| `Aggressive_Brawler` | Rush and overwhelm — maximize damage output |
| `Cautious_Skirmisher` | Hit-and-run, prioritize survival |
| `Apex_Predator` | Calculated, uses all tools; targets weak points |
| `Pack_Hunter` | Coordinates with allies; flanks and isolates |

### 7.3 Anatomy Drops (`Mechanics/anatomy_drops.json`) — 26 entries

Harvestable body part slot definitions. Defines what body part drops what consumable category on entity defeat.

### 7.4 Harvest Types (`Mechanics/harvest_types.json`) — 9 entries

Defines the mechanical actions used to harvest a defeated entity (e.g., Skin, Butcher, Extract).

### 7.5 Biological Upgrades (`Mechanics/biological_upgrades.json`) — 8 entries

Upgrade paths that modify entity stats or grant skills upon growth/mutation events.

### 7.6 Loot Quality (`Mechanics/loot_quality.json`) — 16 entries

Quality tiers for harvested materials (applied as a multiplier on yield/value):

`High` → `Medium` → `Low` | `Shattered` → `Cracked` → `Chipped` → `Standard` → `Intact` → `Pristine` → `Flawless` | `Rotting` → `Tainted` → `Mangled` → `Prime` → `Exquisite` → `Perfect`

### 7.7 Leveling Rules (`Mechanics/leveling_rules.json`)

Contains `base_leveling_rules` and `mutations_by_tag` — drives how entities scale stats and gain mutations as they level up.

### 7.8 Growth Stages (`Mechanics/growth_stages/`)

**Size Indices:**

| Size | Index Value |
|---|---|
| Tiny | 2 |
| Small | 3 |
| Medium | 4 |
| Large | 6 |
| Huge | 8 |
| Colossal | 16 |

`size_index` feeds directly into `hp_max` and `natural_armor` formulas.

---

## 8. World Data

### 8.1 Biomes (`World/biomes.json`) — 13 entries

| Key | Name |
|---|---|
| Ocean | Open Ocean |
| Ice_Cap | Ice Cap |
| Tundra | Tundra |
| Temperate_Forest | Temperate Forest |
| Arid_Desert | Arid Desert |
| *(+8 more)* | |

Each biome defines: `terrain_flags`, `climate`, `adaptation_rules` (skills + mods for spawned entities), `payloads` (environmental hazards), `resource_tags`.

### 8.2 Temperature Bands (`World/temperature_bands.json`) — 8 entries

`Freezing` → `Cold` → `Cool` → `Moderate` → `Warm` → `Hot` → `Extreme_Heat` → `Lethal_Heat`

All implemented via ambient Status Effect Payloads (`chance_per_tick: 1.0`).

### 8.3 Weather Types (`World/weather_types.json`) — 11 entries

`Clear`, `Windy`, `Raining`, `Overcast`, `Blizzard`, `Thunderstorm`, `Fog`, `Sandstorm`, `Acid_Rain`, `Ash_Fall`, `Aurora`

Each defines `terrain_additions` (temporary tile mutations) and `payloads`.

### 8.4 Spawning Rules (`World/spawning_rules/`)

- `group_scaling.json` — 6 entries: defines how group sizes scale with entity tier/level
- `size_limits.json` — 6 entries: maps size categories to spawn constraints per biome

---

## 9. Skills & Status Effects Summary

### Skills (`GameData/skills.json`) — 217 entries

**Schema:**
```json
"<Skill_Name>": {
  "description": "string",
  "types":       ["string"],     // From skill_types.json
  "range":       "string|int",   // "Melee", "Audible", or grid distance
  "mods":        [ModObject],
  "payloads": [{
    "id":             "StatusEffect_ID",
    "chance_per_tick": 0.0–1.0,
    "duration_ticks":  int
  }]
}
```

**Notable skill categories (by `types` field):**
- `Melee_Attack` + `Natural_Weapon` — direct damage
- `Ranged_Attack` — projectile/breath attacks
- `Passive` — permanent mods applied at init
- `Vocal` — sonic/roar effects
- `Secretion` — venom, poison, acid
- `Defensive` — buffs, shields, counters
- `Locomotion` — movement abilities (Burrow, Leap, Phase)
- `Social` — pack coordination, rallying

### Status Effects (`GameData/Mechanics/status_effects.json`) — 93 entries

**Schema:**
```json
"<Effect_ID>": {
  "description":        "string",
  "blocks_skill_types": ["string"],
  "mods":               [ModObject]
}
```

The `blocks_skill_types` array is the primary crowd-control mechanism — a stunned entity can have all `Melee_Attack` and `Locomotion` skills blocked simultaneously.

---

## 10. Global Data Summary Table

| Collection | File / Path | Entry Count | Status |
|---|---|---|---|
| **SKILLS** | `GameData/skills.json` | **217** | ✅ Complete |
| **STATUS EFFECTS** | `Mechanics/status_effects.json` | **93** | ✅ Complete |
| **BASE STATS** | `Definitions/base_stats.json` | **15** | ✅ Complete |
| **DERIVED STATS** | `Definitions/derived_stats.json` | **37** | ✅ Complete |
| **DAMAGE TYPES** | `types_and_ranges/damage_types.json` | **16** | ✅ Complete |
| **TERRAIN TYPES** | `types_and_ranges/terrain_types.json` | **31** | ✅ Complete |
| **SKILL TYPES** | `types_and_ranges/skill_types.json` | **20** | ✅ Complete |
| **TRAVERSAL TYPES** | `types_and_ranges/traversal_types.json` | **22** | ✅ Complete |
| **VISION TYPES** | `types_and_ranges/vision_types.json` | **12** | ✅ Complete |
| **HEARING TYPES** | `types_and_ranges/hearing_types.json` | **8** | ✅ Complete |
| **SCENT TYPES** | `types_and_ranges/scent_types.json` | **6** | ✅ Complete |
| **COMBAT TAGS** | `Definitions/combat_tags.json` | **6** | ✅ Complete |
| **BIOMES** | `World/biomes.json` | **13** | ✅ Complete |
| **WEATHER TYPES** | `World/weather_types.json` | **11** | ✅ Complete |
| **TEMPERATURE BANDS** | `World/temperature_bands.json` | **8** | ✅ Complete |
| **SPAWNING: GROUP** | `World/spawning_rules/group_scaling.json` | **6** | ✅ Complete |
| **SPAWNING: SIZE** | `World/spawning_rules/size_limits.json` | **6** | ✅ Complete |
| **BEHAVIORS** | `Mechanics/behaviors.json` | **4** | ✅ Complete |
| **ANATOMY DROPS** | `Mechanics/anatomy_drops.json` | **26** | ✅ Complete |
| **HARVEST TYPES** | `Mechanics/harvest_types.json` | **9** | ✅ Complete |
| **BIO UPGRADES** | `Mechanics/biological_upgrades.json` | **8** | ✅ Complete |
| **LOOT QUALITY** | `Mechanics/loot_quality.json` | **16** | ✅ Complete |
| **PATTERNS** | `Core/appearance/patterns.json` | **7** | ✅ Complete |
| **PIGMENTATION** | `Core/appearance/pigmentation.json` | **7** | ✅ Complete |
| **PREFIXES** | `GameData/prefixes.json` | **7** | ✅ Complete |
| **CONSUMABLE CATS** | `GameData/consumable_categories.json` | **8** | ✅ Complete |
| **SIZE INDICES** | `growth_stages/size_indices.json` | **6** | ✅ Complete |
| **LINEAGES** | (32 lineage files per part) | **32** | ✅ Complete |
| **ENTITY PARTS (Beast)** | 13 part directories × 32 lineages | **~11,000+ entries** | ✅ Complete |
| **Flora/Canopy** | `Entities/Flora/canopy/` | — | 🔶 Stub |
| **Flora/Roots** | `Entities/Flora/roots/` | — | 🔶 Stub |
| **Geological/Composition** | `Entities/Geological/composition/` | — | 🔶 Stub |
| **Geological/Formation** | `Entities/Geological/formation/` | — | 🔶 Stub |

### Entity Part Total Estimate

| Part Category | Parts | Avg Entries/File | Lineages | Total Entries |
|---|---|---|---|---|
| Core (chassis + integument) | 2 | ~11 | 32 | ~704 |
| Core appearance | 2 files (universal) | 7 | 1 | 14 |
| Cephalon | 5 | ~11 | 32 | ~1,760 |
| Appendages | 6 | ~11 | 32 | ~2,112 |
| **TOTAL BEAST ENTRIES** | **15 part types** | | **32 lineages** | **~4,590** |

---

## Appendix: Open/Stub Systems

The following systems have directory structure created but no lineage-specific data yet:

| System | Path | Notes |
|---|---|---|
| **Flora** | `Entities/Flora/canopy/` + `roots/` | Only `common.json` skeleton exists |
| **Geological** | `Entities/Geological/composition/` + `formation/` | Only `common.json` skeleton exists |
| **Growth Stages** | `Mechanics/growth_stages/stages.json` | Schema only (`{"mods": []}`) |

These represent the next major expansion areas of the project.
