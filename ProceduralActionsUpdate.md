# Architecture Design: Procedural Action & Status Assembly
## MadCore RPG — Implementation Reference

> **Status:** Implementation-Ready. All entries fully enumerated.
> **Cross-referenced against:** `skills.json` (217), `status_effects.json` (93), `skill_types.json` (20), `damage_types.json` (16)

---

## 1. Architecture Overview

Instead of 217 hardcoded skills, the engine compiles actions at entity-generation time from four orthogonal primitives:

```
Action Template  +  Mutator(s)  →  Compiled Skill
     (Verb)          (Adjectives)
Status Template  +  Parameters  →  Compiled Status Effect
```

| Primitive | File | Count |
|---|---|---|
| Targeting Shapes | `Definitions/types_and_ranges/targeting_shapes.json` | 9 |
| Targeting Affections | `Definitions/types_and_ranges/targeting_affections.json` | 5 |
| Action Templates | `GameData/action_templates.json` | 21 |
| Mutators | `GameData/mutators.json` | 34 |
| Status Templates | `GameData/Mechanics/status_templates.json` | 14 |

---

## 2. Targeting Shapes — 9 Entries

```json
{
  "Self":           { "description": "Affects only the casting entity.",                                    "shape_param_fields": [] },
  "Single_Target":  { "description": "Affects exactly one entity within range.",                             "shape_param_fields": [] },
  "Multi_Target":   { "description": "Affects up to N distinct entities in range.",                          "shape_param_fields": ["max_targets"] },
  "Line":           { "description": "All entities on a linear vector from caster.",                         "shape_param_fields": ["width"] },
  "Cone":           { "description": "All entities within a forward arc from caster.",                       "shape_param_fields": ["angle_degrees"] },
  "Radius_Self":    { "description": "Expands outward from caster to radius.",                               "shape_param_fields": [] },
  "Radius_Target":  { "description": "Expands from a chosen distant coordinate.",                            "shape_param_fields": [] },
  "Chain":          { "description": "Hits initial target, jumps to nearest valid entities.",                 "shape_param_fields": ["max_jumps", "falloff"] },
  "Wall":           { "description": "Creates a linear segment obstacle placed on the grid.",                "shape_param_fields": ["length", "thickness"] }
}
```

---

## 3. Targeting Affections — 5 Entries

```json
{
  "Hostile":              { "description": "Enemy factions only." },
  "Friendly":             { "description": "Allied factions, including caster." },
  "Friendly_Exclude_Self":{ "description": "Allied factions, excluding caster." },
  "All":                  { "description": "Any entity in shape." },
  "All_Exclude_Self":     { "description": "Any entity in shape except caster." }
}
```

---

## 4. Range Object Schema

All action templates use `range_object` instead of a bare string.

```json
"range_object": {
  "alias":        null,
  "min":          0,
  "base":         0,
  "max":          30,
  "surface_only": false,
  "shape_param":  {}
}
```

| Field | Values / Notes |
|---|---|
| `alias` | `"Melee"` (0–5 ft), `"Audible"` (→ entity `hearing_range`), `"Sight"` (→ entity `vision_range`), `"Self"` |
| `min` | Minimum range. `0` = adjacent targets valid |
| `base` / `max` | Operating / maximum grid distance |
| `surface_only` | `true` = only hits ground tiles (webs, tremorsense, geyser) |
| `shape_param` | `Cone: {angle_degrees:90}`, `Line: {width:1}`, `Chain: {max_jumps:3, falloff:0.5}`, `Wall: {length:10, thickness:1}`, `Multi_Target: {max_targets:3}` |

---

## 5. Action Templates — 21 Entries

### Schema

```json
"<Template_ID>": {
  "description":      "string",
  "types":            ["skill_type_key"],
  "trigger_type":     "Active | Passive | Reaction",
  "target_shape":     "shape_key",
  "target_affection": "affection_key",
  "range_object":     { "alias": null, "min": 0, "base": 0, "max": 0, "surface_only": false, "shape_param": {} },
  "base_expression":  "dice_expr",
  "base_damage_type": "damage_type_key",
  "stat_dependencies": ["stat_key"]
}
```

> `base_damage_type` is always physical. Elemental Mutators override it at compile time.
> `trigger_type: Passive` = applied at entity init; never cast. Used for permanent auras.

### Full Template List

```json
{
  "Melee_Strike": {
    "description": "Basic close-quarters appendage attack.",
    "types": ["Melee_Attack", "Natural_Weapon"],
    "trigger_type": "Active",
    "target_shape": "Single_Target",
    "target_affection": "Hostile",
    "range_object": { "alias": "Melee", "min": 0, "base": 0, "max": 5, "surface_only": false, "shape_param": {} },
    "base_expression": "1d6 + str",
    "base_damage_type": "Bludgeoning",
    "stat_dependencies": ["str"]
  },
  "Cleaving_Strike": {
    "description": "Wide arc strike hitting all targets in a forward cone.",
    "types": ["Melee_Attack", "Area_Of_Effect"],
    "trigger_type": "Active",
    "target_shape": "Cone",
    "target_affection": "Hostile",
    "range_object": { "alias": "Melee", "min": 0, "base": 0, "max": 5, "surface_only": false, "shape_param": { "angle_degrees": 90 } },
    "base_expression": "1d4 + str",
    "base_damage_type": "Slashing",
    "stat_dependencies": ["str"]
  },
  "Leap_Slam": {
    "description": "Caster jumps to target location, dealing AoE damage on landing.",
    "types": ["Melee_Attack", "Movement", "Area_Of_Effect"],
    "trigger_type": "Active",
    "target_shape": "Radius_Self",
    "target_affection": "Hostile",
    "range_object": { "alias": null, "min": 0, "base": 0, "max": 20, "surface_only": false, "shape_param": {} },
    "base_expression": "2d4 + str",
    "base_damage_type": "Bludgeoning",
    "stat_dependencies": ["str"]
  },
  "Charge_Strike": {
    "description": "Caster moves at speed toward a single target and delivers a powerful impact.",
    "types": ["Melee_Attack", "Movement"],
    "trigger_type": "Active",
    "target_shape": "Single_Target",
    "target_affection": "Hostile",
    "range_object": { "alias": null, "min": 5, "base": 5, "max": 20, "surface_only": false, "shape_param": {} },
    "base_expression": "1d8 + str",
    "base_damage_type": "Bludgeoning",
    "stat_dependencies": ["str"]
  },
  "Projectile_Launch": {
    "description": "Fires a single physical or biological projectile at range.",
    "types": ["Ranged_Attack", "Natural_Weapon"],
    "trigger_type": "Active",
    "target_shape": "Single_Target",
    "target_affection": "Hostile",
    "range_object": { "alias": null, "min": 5, "base": 30, "max": 60, "surface_only": false, "shape_param": {} },
    "base_expression": "1d6 + dex",
    "base_damage_type": "Piercing",
    "stat_dependencies": ["dex"]
  },
  "Fluid_Ejection": {
    "description": "Expels a biological substance (breath, acid, venom) in a forward cone.",
    "types": ["Ranged_Attack", "Breath_Weapon"],
    "trigger_type": "Active",
    "target_shape": "Cone",
    "target_affection": "Hostile",
    "range_object": { "alias": null, "min": 0, "base": 0, "max": 30, "surface_only": false, "shape_param": { "angle_degrees": 90 } },
    "base_expression": "1d6 + con",
    "base_damage_type": "Bludgeoning",
    "stat_dependencies": ["con"]
  },
  "Energy_Beam": {
    "description": "An instant, focused vector of energy discharged from the entity.",
    "types": ["Ranged_Attack", "Damage"],
    "trigger_type": "Active",
    "target_shape": "Line",
    "target_affection": "Hostile",
    "range_object": { "alias": null, "min": 0, "base": 0, "max": 60, "surface_only": false, "shape_param": { "width": 1 } },
    "base_expression": "1d6 + int",
    "base_damage_type": "Bludgeoning",
    "stat_dependencies": ["int"]
  },
  "Channeled_Beam": {
    "description": "Sustained beam held for multiple ticks; deals damage each tick while maintained.",
    "types": ["Ranged_Attack", "Damage"],
    "trigger_type": "Active",
    "target_shape": "Line",
    "target_affection": "Hostile",
    "range_object": { "alias": null, "min": 0, "base": 0, "max": 40, "surface_only": false, "shape_param": { "width": 1, "ticks_held": 3 } },
    "base_expression": "1d4 + int",
    "base_damage_type": "Bludgeoning",
    "stat_dependencies": ["int"]
  },
  "Volley": {
    "description": "Rains multiple projectiles down on an area from above.",
    "types": ["Ranged_Attack", "Area_Of_Effect"],
    "trigger_type": "Active",
    "target_shape": "Radius_Target",
    "target_affection": "Hostile",
    "range_object": { "alias": null, "min": 10, "base": 10, "max": 60, "surface_only": false, "shape_param": {} },
    "base_expression": "1d4 + dex",
    "base_damage_type": "Piercing",
    "stat_dependencies": ["dex"]
  },
  "Ground_Eruption": {
    "description": "Forces something up through the surface at a target location (web floor, geyser, roots).",
    "types": ["Ranged_Attack", "Area_Of_Effect"],
    "trigger_type": "Active",
    "target_shape": "Radius_Target",
    "target_affection": "Hostile",
    "range_object": { "alias": null, "min": 0, "base": 0, "max": 40, "surface_only": true, "shape_param": {} },
    "base_expression": "1d6 + str",
    "base_damage_type": "Bludgeoning",
    "stat_dependencies": ["str"]
  },
  "Targeted_Eruption": {
    "description": "Summons a concentrated hazard or explosion at a distant target coordinate.",
    "types": ["Ranged_Attack", "Damage", "Area_Of_Effect"],
    "trigger_type": "Active",
    "target_shape": "Radius_Target",
    "target_affection": "Hostile",
    "range_object": { "alias": null, "min": 5, "base": 5, "max": 60, "surface_only": false, "shape_param": {} },
    "base_expression": "2d6 + int",
    "base_damage_type": "Bludgeoning",
    "stat_dependencies": ["int"]
  },
  "Aura_Emanation": {
    "description": "An active cast that pulses a heal or utility effect to all nearby allies for a duration.",
    "types": ["Healing", "Area_Of_Effect"],
    "trigger_type": "Active",
    "target_shape": "Radius_Self",
    "target_affection": "Friendly",
    "range_object": { "alias": null, "min": 0, "base": 0, "max": 20, "surface_only": false, "shape_param": {} },
    "base_expression": "1d4 + wis",
    "base_damage_type": "Healing",
    "stat_dependencies": ["wis"]
  },
  "Passive_Aura": {
    "description": "A permanently-active aura applied at entity initialisation. Never expires.",
    "types": ["Passive", "Enhancement"],
    "trigger_type": "Passive",
    "target_shape": "Radius_Self",
    "target_affection": "All",
    "range_object": { "alias": null, "min": 0, "base": 0, "max": 10, "surface_only": false, "shape_param": {} },
    "base_expression": "0",
    "base_damage_type": null,
    "stat_dependencies": []
  },
  "Vocal_Resonance": {
    "description": "Emits a shockwave of sound affecting all entities in range regardless of faction.",
    "types": ["Vocal", "Area_Of_Effect"],
    "trigger_type": "Active",
    "target_shape": "Radius_Self",
    "target_affection": "All",
    "range_object": { "alias": "Audible", "min": 0, "base": 0, "max": 0, "surface_only": false, "shape_param": {} },
    "base_expression": "1d4 + cha",
    "base_damage_type": "Sonic",
    "stat_dependencies": ["cha"]
  },
  "Environmental_Shift": {
    "description": "Alters terrain at a distant coordinate (freeze water, create mud, ignite foliage).",
    "types": ["Action", "Area_Of_Effect"],
    "trigger_type": "Active",
    "target_shape": "Radius_Target",
    "target_affection": "All",
    "range_object": { "alias": null, "min": 0, "base": 0, "max": 40, "surface_only": true, "shape_param": {} },
    "base_expression": "0",
    "base_damage_type": null,
    "stat_dependencies": []
  },
  "Construct_Barrier": {
    "description": "Creates a physical or elemental linear wall obstacle on the grid.",
    "types": ["Construct", "Area_Of_Effect"],
    "trigger_type": "Active",
    "target_shape": "Wall",
    "target_affection": "All",
    "range_object": { "alias": null, "min": 0, "base": 0, "max": 20, "surface_only": false, "shape_param": { "length": 10, "thickness": 1 } },
    "base_expression": "0",
    "base_damage_type": null,
    "stat_dependencies": []
  },
  "Bodily_Mutation": {
    "description": "The entity alters its own physical form — hardening skin, deploying camouflage, phasing.",
    "types": ["Stance", "Defense"],
    "trigger_type": "Active",
    "target_shape": "Self",
    "target_affection": "Friendly",
    "range_object": { "alias": "Self", "min": 0, "base": 0, "max": 0, "surface_only": false, "shape_param": {} },
    "base_expression": "0",
    "base_damage_type": null,
    "stat_dependencies": []
  },
  "Teleportation": {
    "description": "Instantly repositions the caster to a valid unoccupied location.",
    "types": ["Movement", "Action"],
    "trigger_type": "Active",
    "target_shape": "Self",
    "target_affection": "Friendly",
    "range_object": { "alias": null, "min": 0, "base": 0, "max": 30, "surface_only": false, "shape_param": {} },
    "base_expression": "0",
    "base_damage_type": null,
    "stat_dependencies": []
  },
  "Summon_Entity": {
    "description": "Spawns a persistent entity or hazard structure at a target location.",
    "types": ["Summon", "Action"],
    "trigger_type": "Active",
    "target_shape": "Radius_Target",
    "target_affection": "Friendly",
    "range_object": { "alias": null, "min": 0, "base": 0, "max": 30, "surface_only": false, "shape_param": {} },
    "base_expression": "0",
    "base_damage_type": null,
    "stat_dependencies": []
  },
  "Retaliation": {
    "description": "Triggered out-of-turn in response to incoming damage. Delivers a counterattack.",
    "types": ["Melee_Attack", "Reaction", "Natural_Weapon"],
    "trigger_type": "Reaction",
    "target_shape": "Single_Target",
    "target_affection": "Hostile",
    "range_object": { "alias": "Melee", "min": 0, "base": 0, "max": 5, "surface_only": false, "shape_param": {} },
    "base_expression": "1d4 + str",
    "base_damage_type": "Bludgeoning",
    "stat_dependencies": ["str"]
  },
  "Counter_Strike": {
    "description": "A defensive parry that reflects or redirects incoming force back at the attacker.",
    "types": ["Defense", "Reaction", "Melee_Attack"],
    "trigger_type": "Reaction",
    "target_shape": "Single_Target",
    "target_affection": "Hostile",
    "range_object": { "alias": "Melee", "min": 0, "base": 0, "max": 5, "surface_only": false, "shape_param": {} },
    "base_expression": "1d6 + dex",
    "base_damage_type": "Bludgeoning",
    "stat_dependencies": ["dex"]
  }
}
```

---

## 6. Mutators — 34 Entries

### Schema

```json
"<Mutator_ID>": {
  "category":        "Physical | Elemental | Utility",
  "description":     "string",
  "overrides":       { "base_damage_type": "string" },
  "adds_mods":       [ModObject],
  "adds_payloads":   [PayloadObject],
  "adds_sub_actions": [],
  "parameters":      {}
}
```

### 6A. Physical Mutators — 6 Entries

```json
{
  "Aspect_Piercing": {
    "category": "Physical",
    "description": "Deep tissue penetration targeting vital organs.",
    "overrides": { "base_damage_type": "Piercing" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Deep_Wound", "chance_per_tick": 0.20, "duration_ticks": 3 }],
    "adds_sub_actions": []
  },
  "Aspect_Slashing": {
    "category": "Physical",
    "description": "Clean, deep severing of muscle and connective tissue.",
    "overrides": { "base_damage_type": "Slashing" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Bleeding", "chance_per_tick": 0.25, "duration_ticks": 4 }],
    "adds_sub_actions": []
  },
  "Aspect_Bludgeoning": {
    "category": "Physical",
    "description": "Heavy kinetic impact that breaks bones and ruptures organs.",
    "overrides": { "base_damage_type": "Bludgeoning" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Concussion", "chance_per_tick": 0.10, "duration_ticks": 2 }],
    "adds_sub_actions": []
  },
  "Aspect_Shredding": {
    "category": "Physical",
    "description": "Frantic surface-level tearing that reduces the target's natural armor.",
    "overrides": { "base_damage_type": "Shredding" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Minor_Laceration", "chance_per_tick": 0.40, "duration_ticks": 2 }, { "id": "Corroded", "chance_per_tick": 0.20, "duration_ticks": 2 }],
    "adds_sub_actions": []
  },
  "Aspect_Hemorrhagic": {
    "category": "Physical",
    "description": "Amplifies bleed severity; each application stacks additional DoT.",
    "overrides": { "base_damage_type": "Slashing" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Bleeding", "chance_per_tick": 0.40, "duration_ticks": 6, "stack": true }],
    "adds_sub_actions": []
  },
  "Aspect_Suffocating": {
    "category": "Physical",
    "description": "Cuts off oxygen supply; bypasses standard armor, drains stamina rapidly.",
    "overrides": { "base_damage_type": "Asphyxiation" },
    "adds_mods": [{ "target": "stamina_regen", "op": "multiply", "expr": "0.0", "stat_dependencies": [] }],
    "adds_payloads": [{ "id": "Suffocation", "chance_per_tick": 0.60, "duration_ticks": 3 }],
    "adds_sub_actions": []
  }
}
```

### 6B. Elemental / Magical Mutators — 13 Entries

```json
{
  "Aspect_Caustic": {
    "category": "Elemental",
    "description": "Infuses with corrosive acid that eats through armor and flesh.",
    "overrides": { "base_damage_type": "Acid" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Corroded", "chance_per_tick": 0.30, "duration_ticks": 4 }],
    "adds_sub_actions": []
  },
  "Aspect_Fiery": {
    "category": "Elemental",
    "description": "Infuses with fire that ignites targets and causes intense burning.",
    "overrides": { "base_damage_type": "Fire" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Ignite", "chance_per_tick": 0.25, "duration_ticks": 4 }],
    "adds_sub_actions": []
  },
  "Aspect_Glacial": {
    "category": "Elemental",
    "description": "Infuses with Cold energy that slows movement and shatters frozen tissue.",
    "overrides": { "base_damage_type": "Cold" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Frostbite", "chance_per_tick": 0.20, "duration_ticks": 4 }],
    "adds_sub_actions": []
  },
  "Aspect_Voltaic": {
    "category": "Elemental",
    "description": "Infuses with high-voltage electricity that stuns the nervous system.",
    "overrides": { "base_damage_type": "Lightning" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Paralyzed", "chance_per_tick": 0.10, "duration_ticks": 2 }, { "id": "Stunned", "chance_per_tick": 0.30, "duration_ticks": 1 }],
    "adds_sub_actions": []
  },
  "Aspect_Venomous": {
    "category": "Elemental",
    "description": "Injects biological toxin causing stat degradation and ongoing HP loss.",
    "overrides": { "base_damage_type": "Poison" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Poisoned", "chance_per_tick": 0.50, "duration_ticks": 5 }],
    "adds_sub_actions": []
  },
  "Aspect_Pathogenic": {
    "category": "Elemental",
    "description": "Carriers a fast-spreading pathogen that decays constitution over time.",
    "overrides": { "base_damage_type": "Disease" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Infected", "chance_per_tick": 0.15, "duration_ticks": 8 }],
    "adds_sub_actions": []
  },
  "Aspect_Necrotic": {
    "category": "Elemental",
    "description": "Dark energy that withers living matter and blocks the body's healing responses.",
    "overrides": { "base_damage_type": "Necrotic" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Withering", "chance_per_tick": 0.20, "duration_ticks": 5 }],
    "adds_sub_actions": []
  },
  "Aspect_Luminous": {
    "category": "Elemental",
    "description": "Blinding purifying light that burns fiendish entities and sears vision.",
    "overrides": { "base_damage_type": "Radiant" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Blinded", "chance_per_tick": 0.15, "duration_ticks": 2 }],
    "adds_sub_actions": []
  },
  "Aspect_Telepathic": {
    "category": "Elemental",
    "description": "Direct mental assault that bypasses physical armor and corrupts cognition.",
    "overrides": { "base_damage_type": "Psychic" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Confusion", "chance_per_tick": 0.10, "duration_ticks": 3 }],
    "adds_sub_actions": []
  },
  "Aspect_Resonant": {
    "category": "Elemental",
    "description": "Concentrated sonic shockwaves that rupture eardrums and shatter rigid structures.",
    "overrides": { "base_damage_type": "Sonic" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Deafened", "chance_per_tick": 0.30, "duration_ticks": 3 }],
    "adds_sub_actions": []
  },
  "Aspect_Aquatic": {
    "category": "Elemental",
    "description": "Crushing high-velocity water pressure that knocks targets prone.",
    "overrides": { "base_damage_type": "Hydraulic" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Prone", "chance_per_tick": 0.40, "duration_ticks": 1 }],
    "adds_sub_actions": []
  },
  "Aspect_Ethereal": {
    "category": "Elemental",
    "description": "Raw unstable arcane energy. Bypasses physical resistances and natural armor.",
    "overrides": { "base_damage_type": "Arcane" },
    "adds_mods": [],
    "adds_payloads": [{ "id": "Mana_Burn", "chance_per_tick": 0.25, "duration_ticks": 2 }],
    "adds_sub_actions": [],
    "flags": ["bypasses_physical_resist"]
  },
  "Aspect_Absolute": {
    "category": "Elemental",
    "description": "Absolute damage that cannot be resisted, shielded, or mitigated in any way.",
    "overrides": { "base_damage_type": "True" },
    "adds_mods": [],
    "adds_payloads": [],
    "adds_sub_actions": [],
    "flags": ["unblockable", "ignores_shields", "ignores_armor"]
  }
}
```

### 6C. Utility Mutators — 15 Entries

```json
{
  "Aspect_Restorative": {
    "category": "Utility",
    "description": "Inverts damage expression into healing. Converts all mods from subtract to add.",
    "overrides": { "base_damage_type": "Healing", "op": "add" },
    "adds_mods": [], "adds_payloads": [], "adds_sub_actions": []
  },
  "Aspect_Cleansing": {
    "category": "Utility",
    "description": "On application, purges all active statuses tagged Debuff or DamageOverTime from targets.",
    "overrides": {},
    "adds_mods": [], "adds_payloads": [],
    "adds_sub_actions": [{ "type": "purge_status_tags", "tags": ["Debuff", "DamageOverTime"] }]
  },
  "Aspect_Corrupting": {
    "category": "Utility",
    "description": "On application, purges all active statuses tagged Buff or Regen from targets.",
    "overrides": {},
    "adds_mods": [], "adds_payloads": [],
    "adds_sub_actions": [{ "type": "purge_status_tags", "tags": ["Buff", "Regen"] }]
  },
  "Aspect_Vampiric": {
    "category": "Utility",
    "description": "On each hit, caster recovers HP equal to 50% of damage dealt.",
    "overrides": {},
    "adds_mods": [], "adds_payloads": [],
    "adds_sub_actions": [{ "type": "on_hit_lifesteal", "lifesteal_percent": 0.50 }]
  },
  "Aspect_Chaining": {
    "category": "Utility",
    "description": "After hitting the primary target, the action jumps to the nearest valid entity, decaying each jump.",
    "overrides": { "target_shape": "Chain" },
    "adds_mods": [], "adds_payloads": [], "adds_sub_actions": [],
    "parameters": { "max_jumps": 3, "falloff": 0.5 }
  },
  "Aspect_Forceful": {
    "category": "Utility",
    "description": "Every hit pushes the target 2 tiles away from the caster.",
    "overrides": {},
    "adds_mods": [], "adds_payloads": [],
    "adds_sub_actions": [{ "type": "force_movement", "direction": "away", "distance": 2 }]
  },
  "Aspect_Grasping": {
    "category": "Utility",
    "description": "Roots the target in place at 100% chance.",
    "overrides": {},
    "adds_mods": [{ "target": "speed_bonus", "op": "set", "expr": "0", "stat_dependencies": [] }],
    "adds_payloads": [{ "id": "Web_Ensnare", "chance_per_tick": 1.0, "duration_ticks": 2 }],
    "adds_sub_actions": []
  },
  "Aspect_Colossal": {
    "category": "Utility",
    "description": "Scales all base_expression dice by the caster's size_index factor.",
    "overrides": {},
    "adds_mods": [], "adds_payloads": [], "adds_sub_actions": [],
    "flags": ["scale_dice_by_size_index"]
  },
  "Aspect_Piercing_Armor": {
    "category": "Utility",
    "description": "Reduces the target's natural_armor by 3 before damage is calculated this hit.",
    "overrides": {},
    "adds_mods": [{ "target": "natural_armor", "op": "subtract", "expr": "3", "target_entity": "target", "stat_dependencies": [] }],
    "adds_payloads": [], "adds_sub_actions": []
  },
  "Aspect_AoE_Pulse": {
    "category": "Utility",
    "description": "On hit, emits a secondary Radius_Self splash at 50% of base damage.",
    "overrides": {},
    "adds_mods": [], "adds_payloads": [],
    "adds_sub_actions": [{ "type": "secondary_aoe", "shape": "Radius_Self", "max": 5, "damage_multiplier": 0.5 }]
  },
  "Aspect_Delayed": {
    "category": "Utility",
    "description": "Action does not fire immediately; executes 2 ticks after cast (telegraphed).",
    "overrides": {},
    "adds_mods": [], "adds_payloads": [], "adds_sub_actions": [],
    "parameters": { "delay_ticks": 2 }
  },
  "Aspect_Persistent": {
    "category": "Utility",
    "description": "Converts a cast payload into a permanent status applied at entity init.",
    "overrides": { "trigger_type": "Passive" },
    "adds_mods": [], "adds_payloads": [], "adds_sub_actions": []
  },
  "Aspect_Proportional": {
    "category": "Utility",
    "description": "Replaces base_expression with a percentage of the target's current HP (execute mechanic).",
    "overrides": {},
    "adds_mods": [], "adds_payloads": [], "adds_sub_actions": [],
    "flags": ["replace_expr_with_target_hp_percent"],
    "parameters": { "percent": 0.15 }
  },
  "Aspect_Stacking": {
    "category": "Utility",
    "description": "Payloads can apply multiple times on the same target. Each stack multiplies intensity by 1.5.",
    "overrides": {},
    "adds_mods": [], "adds_payloads": [], "adds_sub_actions": [],
    "parameters": { "max_stacks": 5, "stack_multiplier": 1.5 }
  },
  "Aspect_Silencing": {
    "category": "Utility",
    "description": "Adds Silenced status — blocks all Vocal skill types for the duration.",
    "overrides": {},
    "adds_mods": [], 
    "adds_payloads": [{ "id": "Silenced", "chance_per_tick": 0.80, "duration_ticks": 2 }],
    "adds_sub_actions": []
  }
}
```

---

## 7. Status Templates — 14 Entries

### Schema

```json
"<Template_ID>": {
  "description":        "string",
  "tags":               ["tag"],
  "blocks_skill_types": ["{variable_or_key}"],
  "mods": [
    { "target": "{variable_or_key}", "op": "string", "expr": "{variable_or_value}", "damage_type": "{variable_or_key}", "stat_dependencies": [] }
  ]
}
```

```json
{
  "Condition_DamageOverTime": {
    "description": "Continuous elemental damage each tick.",
    "tags": ["Debuff", "DamageOverTime"],
    "blocks_skill_types": [],
    "mods": [{ "target": "hp", "op": "subtract", "expr": "{dot_intensity}", "damage_type": "{dot_type}", "stat_dependencies": [] }]
  },
  "Condition_Incapacitated": {
    "description": "A disabling condition that prevents a specified set of actions.",
    "tags": ["Debuff", "CrowdControl"],
    "blocks_skill_types": ["{blocked_actions}"],
    "mods": [{ "target": "evasion", "op": "set", "expr": "0", "stat_dependencies": [] }]
  },
  "Condition_StatModifier": {
    "description": "Temporarily modifies a single stat. Buff or Debuff depending on sign.",
    "tags": ["{modifier_tag}"],
    "blocks_skill_types": [],
    "mods": [{ "target": "{stat_key}", "op": "{op}", "expr": "{mod_expr}", "stat_dependencies": [] }]
  },
  "Condition_Regeneration": {
    "description": "Restores HP each tick over the duration.",
    "tags": ["Buff", "Regen"],
    "blocks_skill_types": [],
    "mods": [{ "target": "hp", "op": "add", "expr": "{regen_expr}", "damage_type": "Healing", "stat_dependencies": [] }]
  },
  "Condition_Shielded": {
    "description": "Intercepts incoming damage as a HP buffer until the shield is depleted.",
    "tags": ["Buff", "Defense"],
    "blocks_skill_types": [],
    "mods": [],
    "shield_pool": "{shield_hp}",
    "shield_drain_types": ["all"]
  },
  "Condition_Vulnerable": {
    "description": "Amplifies incoming damage of a specified type by a multiplier.",
    "tags": ["Debuff"],
    "blocks_skill_types": [],
    "mods": [],
    "damage_amplification": { "damage_type": "{weakness_type}", "multiplier": "{multiplier}" }
  },
  "Condition_ForcedMovement": {
    "description": "Pushes or pulls the entity a number of tiles in a specified direction.",
    "tags": ["Debuff", "CrowdControl"],
    "blocks_skill_types": ["Movement"],
    "mods": [{ "target": "evasion", "op": "multiply", "expr": "0.5", "stat_dependencies": [] }],
    "force_move": { "direction": "{direction}", "distance": "{distance}" }
  },
  "Condition_SensoryImpairment": {
    "description": "Reduces or zeroes a perception-related stat (vision, hearing, scent).",
    "tags": ["Debuff", "Perception"],
    "blocks_skill_types": [],
    "mods": [{ "target": "{sense_stat}", "op": "{op}", "expr": "{amount}", "stat_dependencies": [] }]
  },
  "Condition_ResourceDrain": {
    "description": "Drains stamina, stamina_regen, or water_retention — not HP — each tick.",
    "tags": ["Debuff", "DamageOverTime"],
    "blocks_skill_types": [],
    "mods": [{ "target": "{resource_stat}", "op": "{op}", "expr": "{drain_expr}", "stat_dependencies": [] }]
  },
  "Condition_ResistanceModifier": {
    "description": "Raises or lowers resistance to a specific damage type.",
    "tags": ["{modifier_tag}"],
    "blocks_skill_types": [],
    "mods": [{ "target": "{resist_stat}", "op": "{op}", "expr": "{amount}", "stat_dependencies": [] }]
  },
  "Condition_AoE_Hazard_Zone": {
    "description": "Applied to a terrain tile; deals a payload to any entity entering or remaining in the zone.",
    "tags": ["Environmental"],
    "blocks_skill_types": [],
    "mods": [],
    "terrain_hazard": { "payload_id": "{hazard_payload_id}", "per_tick_chance": "{per_tick_chance}" }
  },
  "Condition_Marked": {
    "description": "Target takes amplified damage of a specified type while the mark persists.",
    "tags": ["Debuff"],
    "blocks_skill_types": [],
    "mods": [],
    "damage_amplification": { "damage_type": "{mark_damage_type}", "multiplier": "{mark_multiplier}" }
  },
  "Condition_Taunt": {
    "description": "Forces the entity to exclusively target the taunter while active.",
    "tags": ["CrowdControl"],
    "blocks_skill_types": [],
    "mods": [],
    "force_target": "{taunter_id}"
  },
  "Condition_Charmed": {
    "description": "Overrides faction affiliation — entity fights for the charmer's side.",
    "tags": ["CrowdControl"],
    "blocks_skill_types": ["Melee_Attack", "Ranged_Attack", "Curse"],
    "mods": [{ "target": "wis", "op": "subtract", "expr": "2", "stat_dependencies": [] }],
    "override_faction": "Friendly"
  }
}
```

---

## 8. Compilation Example

**"The Fae Matriarch"** casts her ultimate:

| Source | Contribution |
|---|---|
| Template | `Aura_Emanation` (Friendly, Radius_Self, `1d4 + wis`, Healing) |
| Mutator 1 | `Aspect_Restorative` — flips hp to add, healing type confirmed |
| Mutator 2 | `Aspect_Cleansing` — purge sub-action for Debuff + DoT tags |
| Mutator 3 | `Aspect_Luminous` — ordinarily adds Blinded; `Friendly` affection means engine drops hostile debuffs and injects `Condition_Shielded` instead |

```json
{
  "id": "skill_compiled_fae_ultimate",
  "display_name": "Luminous Restorative Purge",
  "types": ["Healing", "Area_Of_Effect", "Enhancement"],
  "trigger_type": "Active",
  "target_shape": "Radius_Self",
  "target_affection": "Friendly",
  "range_object": { "alias": null, "min": 0, "base": 0, "max": 40, "surface_only": false, "shape_param": {} },
  "mods": [
    { "target": "hp", "op": "add", "expr": "2d6 + wis", "damage_type": "Healing", "stat_dependencies": ["wis"] }
  ],
  "payloads": [
    { "id": "Condition_Shielded", "chance_per_tick": 1.0, "duration_ticks": 3, "parameters": { "shield_hp": "wis * 2" } }
  ],
  "purges_status_tags": ["Debuff", "DamageOverTime"]
}
```

---

## 9. Action Items

### 🔴 Critical (fix before migration)

| Task | Detail |
|---|---|
| Fix `Blind` typo in `Ink Cloud` | → rename payload to `Blinded` |
| Add `Irritated` to `status_effects.json` | Used by `Bristle_Shed` — `sense_bonus subtract 2`, `vision_range multiply 0.8` |
| Add `Pulled` to `status_effects.json` | Used by `Tongue_Lash` — `evasion multiply 0.5`, blocks `Movement` 1 tick |
| Add `Silenced` to `status_effects.json` | Used by `Throat_Clamp` — blocks `Vocal` |
| Add 5 skill types to `skill_types.json` | `Action`, `Area_Of_Effect`, `Damage`, `Defense`, `Reaction` |
| Add 3 damage types to `damage_types.json` | `Asphyxiation`, `True`, `Healing` |

### 🟡 Required for Procedural System

| Task |
|---|
| Create `targeting_shapes.json` (9 entries) |
| Create `targeting_affections.json` (5 entries) |
| Create `action_templates.json` (21 entries) |
| Create `mutators.json` (34 entries) |
| Create `status_templates.json` (14 entries) |
| Add `"tags": []` to all 93 `status_effects.json` entries (tag map in audit doc) |

### 🟢 Polish

| Task |
|---|
| Standardise all 217 skill `range` strings → `range_object` schema |
| Fix `Throw` range `"20/60"` → `{ "min": 20, "max": 60 }` |
| Fix `Tremorsense` range `"60ft_Surface"` → `{ "max": 60, "surface_only": true }` |
| Fix `"Audible"` range skills → `{ "alias": "Audible" }` |