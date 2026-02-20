📊 SYSTEM REGISTRY TRACKER & ARCHITECTURE ROADMAP

CURRENT STATUS: The base Skills and Status Effects dictionaries have been successfully generated and decoupled.
Below is the registry of new stat targets discovered during the Forge process, followed by the Engine Scaling Roadmap.

Pending Core Stats to Define (For base_stats.json & derived_stats.json)

sense_bonus

acrobatics_bonus

natural_armor

fire_resist

cold_resist

poison_resist

necrotic_resist

radiant_resist

arcane_resist

water_retention

stamina_regen

hp_regen

🚀 ROADMAP: ENGINE SCALING & DYNAMIC RPG SYSTEMS

1. Dynamic Expression Evaluation (Stat Scaling)

The Problem: Currently, the expr key in our mods uses hardcoded dice math (e.g., "expr": "1d6 + 2"). This does not scale as entities grow stronger.
The Solution: * Upgrade the expression parser to read core stats and derived stats dynamically.

Introduce a stat_dependencies array to skills/statuses. The engine will query these specific stats from the Entity, inject them into the formula, and then evaluate the expr.

Proposed Schema Update Example:

"mods": [
  { 
    "target": "hp", 
    "op": "subtract", 
    "expr": "1d6 + (str * 1.5)", 
    "stat_dependencies": ["str"] 
  }
]


2. Payload Standardization vs. Skill Variation

The Rule of Core Targets: We must strictly avoid creating "fluff" stats (e.g., no poisonStat or acidicPoisonStat). All damage-over-time effects (whether from a Toxic Spore or a Venomous Bite) should cast the standardized Poisoned status, which strictly targets hp.
How we achieve uniqueness:
If multiple skills apply the same status effect, we differentiate them by:

Mathematical Scaling: (e.g., One scales with dex, another with int).

Payload Weighting: Altering the chance_per_tick or duration_ticks.

Compound Payloads: Adding a secondary effect (e.g., a Venomous Bite also applies Paralyzed).

Flavor Text Only: If mechanically identical, retaining unique names (like Fin Slash vs Tail Swipe) is perfectly valid purely for entity flavor and narrative logs.

3. AI Behavioral Trees & Conditional Logic

The Goal: Move away from hardcoded AI routines into a data-driven Behavioral Tree.

AI branches will use condition nodes that query the Entity's current ECS state.

Conditions will check: Current hp thresholds, active combat_tags (e.g., is the target Breaks_Stealth?), presence of specific prefixes, or currently active status_effects.

4. Leveling Architecture & Mutation Trees

The Goal: Ensure creatures remain viable threats across a full RPG progression curve without needing duplicate JSON entries (e.g., avoiding Goblin_Lvl_1, Goblin_Lvl_10).

Level as a Variable: The integer level will become a globally readable variable inside any "expr" formula.

Leveling Trees: Introduce a system (similar to biome adaptation rules) where reaching specific level thresholds automatically injects new elements into the entity's mods and payloads arrays, scaling their damage output and stats procedurally.