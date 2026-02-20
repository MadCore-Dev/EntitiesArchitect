## 🗺️ MASTER REFACTORING ROADMAP

**Phase 1: World Systems Overhaul**
* **Goal:** Standardize environment and global conditions.
* **Tasks:** Refactor `terrain_types.json`, `temperature_bands.json`, `weather_types.json`, and `biomes.json`. 
* **Key Fix:** Remove raw `mods` arrays from terrain/temperature and shift them into `payloads` that cast hidden, indefinite Status Effects to strictly follow the "Everything is a Payload" architecture.

**Phase 2: Skills & Statuses Ecosystem (Payload Standardization)**
* **Goal:** Finalize the mechanical vocabulary of the engine.
* **Tasks:** Clean up and standardize `skills.json`, `status_effects.json`, `damage_types.json`, `skill_types.json`, `vision_types.json`, and `traversal_types.json`. 
* **Key Fix:** Ensure all damage-over-time or status variations adhere to standard core targets (e.g., using Mathematical Scaling or Compound Payloads rather than creating "fluff" stats).

**Phase 3: Stats Registration & Dynamic Scaling**
* **Goal:** Formalize all mathematical targets and upgrade the expression parser.
* **Tasks:** * Update `base_stats.json` and `derived_stats.json` with newly discovered targets (`sense_bonus`, `water_retention`, elemental resistances, etc.).
  * **Dynamic Expressions:** Introduce a `stat_dependencies` array to skills/statuses to allow the engine to query specific stats for dynamic math (e.g., `"expr": "1d6 + (str * 1.5)"`).

**Phase 4: Advanced Engine Systems (AI & Progression)**
* **Goal:** Establish behavioral logic and scaling blueprints before generating entity data.
* **Tasks:** * **AI Behavioral Trees:** Move away from hardcoded routines. Define data-driven AI branches and condition nodes that query the Entity's ECS state (HP thresholds, active `combat_tags`, active status effects).
* **Leveling & Mutation Architecture:** This will also have a tree structure similar to the ai branches depending on tags/behaviours and stuff which stats will have higher probability of increase from allowed stat points pool that level provides. Introduce 'Level' as a globally readable variable inside `expr` formulas. Define threshold rules that automatically inject new elements into an entity's mods/payloads as they scale, preventing duplicate JSON entries (e.g., no "Goblin_Lvl_10").

**Phase 5: Validation Rules**
* **Goal:** Enforce engine stability and structural laws before mass-producing data.
* **Tasks:** Update `validation_rules.json`. Define the mandatory base stats every living entity must possess and establish the physical component requirements (e.g., must possess a Chassis and Cranium).

**Phase 6: The Entity Lineage Expansion**
* **Goal:** Break down monolithic component files into modular, biologically categorized directories.
* **Tasks:** Replace individual JSON files (e.g., `cranium.json`, `eyes.json`, `maw.json`, `drops.json`) with directories of the same name.
* **Sub-Structure:** Inside each component directory, populate separate JSON files based on evolutionary lineages to ensure highly varied and scalable data generation:
  * `canine.json`
  * `feline.json`
  * `ursine.json`
  * `ungulates.json`
  * `reptiles.json`
  * `birds.json`
  * `insects.json`
  * `primates.json`
  * `marine_life.json`
  * `rodents.json`
  * `mustelids.json`
  * `marsupials.json`
  * `amphibians.json`