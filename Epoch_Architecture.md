# Epoch Engine: Core Architecture & Data Structure

## 1. Design Philosophy
The Epoch Engine operates on a **Pure Component System** driven by **Derived Stats**. 
- **Entities** are containers of specialized components (Chassis, Cranium, Arms, etc.).
- **Components** provide **Base Stats** (Inputs) via modifiers.
- **The Engine** calculates **Derived Stats** (Outputs) using defined formulas.

## 2. The Stat System

### A. Base Stats (Inputs)
Defined in `GameData/Definitions/base_stats.json`.
- `str`, `dex`, `con`, `int`, `wis`, `cha`
- `size_index` (1-20 scale)
- `natural_armor`
- `speed_bonus`

### B. Derived Stats (Outputs)
Defined in `GameData/Definitions/derived_stats.json` with executable formulas.
- `hp_max` = `(size_index * 2) * con`
- `speed` = `(size_index * 5) + (dex * 2) + speed_bonus`
- `ac` = `10 + natural_armor + dex`
- `perception` = `10 + wis + sense_bonus`

## 3. The Universal Modifier System
All changes to an entity's state are delivered via **Effect Payloads** containing a `mods` array.
```json
"mods": [
  { "target_stat": "str", "value": 2, "operation": "add" },
  { "target_stat": "hp", "value": 5, "operation": "subtract", "roll": "1d6", "damage_type": "Fire" }
]
```

## 4. Directory Structure
```
GameData/
├── Definitions/            # The Rulebook (Stats, Formulas, Ops)
│   ├── base_stats.json
│   ├── derived_stats.json
│   └── ...
├── Mechanics/              # Game Logic & Tables
│   ├── status_effects.json # Runtime conditions
│   ├── anatomy_drops.json  # Loot & Skill mapping
│   └── ...
├── World/                  # Environment
│   ├── biomes.json
│   └── spawning_rules.json
├── Entities/               # Component Libraries
│   ├── Core/               # Essential parts (Chassis, Integument)
│   ├── Cephalon/           # Head parts
│   ├── Appendages/         # Limbs & Wings
│   └── ...
├── skills.json             # All Actions/Attacks
├── prefixes.json           # Procedural Modifiers
└── entities.json           # Blueprints
```

## 5. Validation Rules
Blueprints must adhere to `GameData/Definitions/validation_rules.json`:
- Must have `Chassis` and `Cranium`.
- Must have non-zero Base Stats (str, dex, etc.).
