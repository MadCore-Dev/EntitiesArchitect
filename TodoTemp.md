# AGENT TASK: Generate MadCore RPG Lineage JSON Files
# Target root: GameData/Entities/

---

## SCHEMA AUTHORITY
All rules follow `Data_Dictionary.md`. Mods use `"expr"` (always a string).

```json
{ "target": "stat_id", "op": "add|subtract|multiply", "expr": "2" }
```

---

## VALID VOCABULARY (EXACT STRINGS ONLY)

### Traversal Types (`traversal` arrays)
Walk, Climb, Swim, Fly, Hover, Glide, Burrow_Earth, Burrow_Rock, Burrow_Ice,
Slither, Hop, Brachiation, Wall_Crawl, Web_Walk, Water_Walk, Slide,
Jet_Propulsion, Benthic_Crawl, Amorphous_Ooze, Levitate, Ethereal_Glide, Teleportation

### Meat Groups (`meat_group`)
White_Meat, Red_Meat, Chitin, Mucus_Sac, Elemental_Essence, Ectoplasm,
Venom_Gland, Bone_Marrow, Fungal_Flesh, Dark_Ichor

### Stat Targets (`target`)
str, dex, con, int, wis, cha, agility, speed_bonus, size_index, perception,
stealth, evasion, initiative, natural_armor, hp, stamina, water_retention,
vision_range, hearing_range, scent_range, jump_distance, reach,
fire_resist, cold_resist, poison_resist, acid_resist, lightning_resist,
necrotic_resist, radiant_resist, arcane_resist, bludgeoning_resist,
piercing_resist, slashing_resist, psychic_resist, disease_resist

### Skills (prefer existing — invent only if necessary)
Acid Spray, Acrobatics, Aerobatics, Ambush, Bite, Block, Blood Frenzy,
Body Slam, Burrow, Camouflage, Claw, Constrict, Counterbalance, Crunch,
Dart, Death Roll, Dig, Directional Tracking, Drain, Echolocation,
Echolocation Blast, Ensnare, Fear, Gnaw, Gore, Grapple, Grip, Headbutt,
Hind Kick, Hibernation, Hop, Incorporeal, Ink Cloud, Intimidate, Iron Grip,
Jaw Snap, Keen Sight, Kick, Leap, Maul, Mucous Skin, Natural Armor,
No Pain, Pack Tactics, Paralyze, Paw Strike, Poison, Pounce, Python Squeeze,
Quill Shoot, Rake, Regeneration, Roll Attack, Scavenger, Screech,
Serrated Bite, Skunk Musk, Slam, Slash, Slime Secretion, Snatch, Soft Step,
Sonic Snap, Spider Climb, Spiked Tail, Sprint, Squeeze, Stability, Stealth,
Sting, Stomp, Suction Grip, Sure-Footed, Tail Swipe, Tail Whip, Tentacle Lash,
Thick Fur, Tracking, Trample, Tremor Sense, Tusk Slash, Vampiric Drain,
Venom Spit, Venomous Bite, Wall Climb

---

## COMPLETE FILE MAP PER LINEAGE

Generate ALL applicable files. Write to exact path under `GameData/Entities/`:

| File Type | Path | `traversal` field? | Extra fields |
|---|---|---|---|
| Chassis | `Core/chassis/<lineage>.json` | ❌ | `tags`, `meat_group`, `slots`, `mods`, `grants_skills`, `description` |
| Integument | `Core/integument/<lineage>.json` | ❌ | `tags`, `mods`, `grants_skills`, `description` |
| Arms | `Appendages/arms/<lineage>.json` | ✅ | `tags`, `traversal`, `mods`, `grants_skills`, `description` |
| Legs | `Appendages/legs/<lineage>.json` | ✅ | `tags`, `traversal`, `mods`, `grants_skills`, `description` |
| Tails | `Appendages/tails/<lineage>.json` | ✅ (often `[]`) | `tags`, `traversal`, `mods`, `grants_skills`, `description` |
| Fins | `Appendages/fins/<lineage>.json` | ✅ | Aquatic lineages only |
| Wings | `Appendages/wings/<lineage>.json` | ✅ | Flying lineages only (Fly, Hover, Glide) |
| Tentacles | `Appendages/tentacles/<lineage>.json` | ✅ | Cephalopod/Aberrant only |
| Cranium | `Cephalon/cranium/<lineage>.json` | ❌ | `tags`, `slots` (eye/ear/maw/nose), `mods`, `grants_skills`, `description` |
| Ears | `Cephalon/ears/<lineage>.json` | ❌ | `tags`, `mods`, `grants_skills`, `description` |
| Eyes | `Cephalon/eyes/<lineage>.json` | ❌ | `tags`, `mods`, `grants_skills`, `description` |
| Maw | `Cephalon/maw/<lineage>.json` | ❌ | `tags`, `mods`, `grants_skills`, `description` |
| Nose | `Cephalon/nose/<lineage>.json` | ❌ | `tags`, `mods`, `grants_skills`, `description` |

> `Core/appearance` is SHARED (only `patterns.json` + `pigmentation.json`). Do NOT create per-lineage appearance files.

**Omit** a file entirely if anatomically invalid:
- No `tails` for ooze, crustacean, vermian (limbless)
- No `arms`/`legs`/`tails` for ooze/slime — use `Amorphous_Ooze` traversal on chassis description only
- No `fins` unless aquatic
- No `wings` unless flying lineage
- No `tentacles` unless cephalopod/aberrant/fae/spectral
- Spectral/Elemental: omit `arms`/`legs`/`tails` if incorporeal; use `Ethereal_Glide` or `Levitate`

---

## SCHEMAS

### Chassis (`Core/chassis/<lineage>.json`)
```json
{
  "Variant_Name": {
    "tags": ["Flesh|Chitin|Bone|etc", "Lineage", "Archetype"],
    "meat_group": ["Red_Meat"],
    "slots": {
      "head": "Cephalon/cranium",
      "integument": "Core/integument",
      "pattern_layer": "Core/appearance",
      "pigment_layer": "Core/appearance",
      "leg_fore_left": "Appendages/legs",
      "leg_fore_right": "Appendages/legs",
      "leg_rear_left": "Appendages/legs",
      "leg_rear_right": "Appendages/legs",
      "tail_main": "Appendages/tails"
    },
    "mods": [{ "target": "str", "op": "add", "expr": "2" }],
    "grants_skills": ["Skill_Name"],
    "description": "2-4 sentence dark fantasy flavor text."
  }
}
```

### Integument (`Core/integument/<lineage>.json`)
```json
{
  "Variant_Name": {
    "tags": ["Fur|Skin|Scales|Chitin|Carapace|Ethereal|etc"],
    "mods": [{ "target": "natural_armor", "op": "add", "expr": "2" }],
    "grants_skills": [],
    "description": "Visual + tactile description."
  }
}
```

### Arms / Legs / Fins / Wings / Tentacles (all Appendages)
```json
{
  "Variant_Name": {
    "tags": ["Arms|Legs|Wings|Fins|Tentacles|etc", "Lineage"],
    "traversal": ["Walk"],
    "mods": [{ "target": "agility", "op": "add", "expr": "2" }],
    "grants_skills": [],
    "description": "Flavor text."
  }
}
```

### Tails (`Appendages/tails/<lineage>.json`)
```json
{
  "Variant_Name": {
    "tags": ["Tail|Fin|Club|Spike|Prehensile|etc"],
    "traversal": [],
    "mods": [{ "target": "balance", "op": "add", "expr": "1" }],
    "grants_skills": [],
    "description": "Flavor text."
  }
}
```

### Cranium (`Cephalon/cranium/<lineage>.json`)
```json
{
  "Variant_Name": {
    "tags": ["Cranium|Skull|Carapace|Beak|etc", "Lineage"],
    "slots": {
      "eye_left": "Cephalon/eyes",
      "eye_right": "Cephalon/eyes",
      "ear_right": "Cephalon/ears",
      "ear_left": "Cephalon/ears",
      "maw_primary": "Cephalon/maw",
      "nose_primary": "Cephalon/nose"
    },
    "mods": [{ "target": "perception", "op": "add", "expr": "1" }],
    "grants_skills": [],
    "description": "Flavor text."
  }
}
```

### Ears / Eyes / Maw / Nose (all Cephalon sensory)
```json
{
  "Variant_Name": {
    "tags": ["Ear|Eye|Maw|Nose|etc", "Lineage", "Archetype"],
    "mods": [{ "target": "perception", "op": "add", "expr": "1" }],
    "grants_skills": [],
    "description": "Flavor text."
  }
}
```

---

## LINEAGES TO GENERATE

### BATCH 1 — Biological Mammals
**`rodent`** — Rat, Mole, Squirrel, Capybara, Porcupine archetypes
- meat: Red_Meat | traversal: Walk, Burrow_Earth, Climb | tags: Rodent
- Porcupine: Quill Shoot | Mole: Burrow_Earth + low vision_range | Capybara: Swim

**`mustelid`** — Weasel, Badger, Wolverine, Otter archetypes
- meat: Red_Meat | traversal: Walk, Burrow_Earth, Swim, Climb
- Wolverine: high str/con + Blood Frenzy | Otter: Swim + Slide | Badger: Burrow_Earth

**`marsupial`** — Opossum, Quoll, Thylacine, Wombat, Kangaroo archetypes
- meat: Red_Meat | traversal: Walk, Hop (kangaroo), Climb (opossum)
- Opossum: Camouflage + No Pain | Wombat: high con + Burrow_Earth

### BATCH 2 — Biological Animals
**`vermian`** — Earthworm, Leech, Bloodworm, Giant Annelid
- meat: White_Meat | NO arms/legs/tails (limbless) | traversal: Slither, Burrow_Earth
- Skills: Leech Latch, Constrict, Drain | cranium slots: omit ears, minimal nose

**`crustacean`** — Crab, Lobster, Isopod, Mantis Shrimp
- meat: Chitin | traversal: Walk, Benthic_Crawl, Swim | integument: Carapace
- Skills: Crab Pinch, Exoskeleton, Slam | tentacles: omit

**`cephalopod`** — Octopus, Squid, Nautilus, Cuttlefish
- meat: Mucus_Sac | NO standard legs/arms — use Appendages/tentacles instead
- traversal: Swim, Jet_Propulsion | Skills: Ink Cloud, Tentacle Lash, Squeeze
- cranium: omit ear slots (no ears); add eye_left/eye_right only

**`chiropteran`** — Cave Bat, Giant Bat, Blood Bat, Spectral Bat
- meat: Red_Meat | traversal: Fly, Hover, Walk | wings: required
- Skills: Echolocation, Silent Flight, Screech | ears: high perception

**`elephantine`** — Forest, Steppe Mammoth, Dwarf, Spiny Megafauna
- meat: Red_Meat | high str/con/size_index | traversal: Walk
- Skills: Trample, Stomp, Tusk Slash, Body Slam

**`hyenid`** — Spotted, Striped, Cave, Giant Scavenger
- meat: Red_Meat | traversal: Walk | Skills: Crunch, Scavenger, Pack Tactics, Blood Frenzy
- maw: bone-crushing variants, high str

**`pholidota`** — Pangolin variants (Burrowing, Aquatic, Giant, Armored)
- meat: Chitin + White_Meat | integument: Keratin Scales
- Skills: Roll Attack, Natural Armor, Dig, Claw | traversal: Walk, Burrow_Earth, Swim

### BATCH 3 — Fantasy Types
**`draconic`** — Whelp, Drake, Wyrm, Elder, Sea Drake, Shadow Drake
- meat: Red_Meat + Venom_Gland | wings required for flying variants
- fire_resist/cold_resist | Skills: Bite, Gore, Tail Whip, Fear, Breath_Weapon (invent if needed)
- traversal: Walk, Fly, Swim (by variant)

**`elemental`** — Fire, Frost, Stone, Storm, Void
- meat: Elemental_Essence ONLY | no standard flesh/bone
- traversal: Levitate (Void/Storm/Fire/Frost), Walk (Stone)
- high elemental resists matching element | no arms/legs for non-Stone variants

**`aberrant`** — Fleshweaver, Eyemass, Void-Crawler, Orifice-Beast
- meat: Dark_Ichor | asymmetric slots (e.g., 3 eye slots, no nose)
- traversal: Amorphous_Ooze or Walk | Skills: Paralyze, Fear, Tentacle Lash
- use Appendages/tentacles for their appendages

**`fae`** — Pixie-Sprite, Sylvan-Titan, Thornling, Dusk-Wisp
- meat: White_Meat | wings for airborne variants
- traversal: Fly, Hover, Walk | Skills: Camouflage, Paralyze, Drain

**`demonkin`** — Impling, Fiend, Archdevil, Hellhound
- meat: Dark_Ichor / Red_Meat | fire_resist high
- traversal: Walk, Fly | Skills: Fear, Vampiric Drain, Claw

**`celestial`** — Seraph, Herald, Radiant-Titan, Warden-Angel
- meat: Ectoplasm | radiant_resist + necrotic_resist | wings required
- traversal: Fly, Hover | Skills: Incorporeal, Regeneration, Fear

**`ooze`** — Amoeba, Gelatinous, Corrosive, Tar, Luminous
- meat: Mucus_Sac | NO arms/legs/tails/cranium — only chassis + integument
- traversal: Amorphous_Ooze | Skills: Slime Secretion, Ensnare, Acid Spray

**`spectral`** — Wisp, Poltergeist, Revenant, Shadow
- meat: Ectoplasm | NO arms/legs/tails — only chassis + integument + cranium (minimal slots)
- traversal: Ethereal_Glide, Levitate | Skills: Incorporeal, Drain, Fear

---

## OUTPUT FORMAT

Label each file with a comment, then output raw JSON only:

```
// GameData/Entities/Core/chassis/rodent.json
{ ... }

// GameData/Entities/Core/integument/rodent.json
{ ... }

// GameData/Entities/Appendages/arms/rodent.json
{ ... }
```

No prose. No explanations between blocks.
If you invent a NEW skill, append one final block:
```
// NEW_SKILLS (append entries to GameData/skills.json)
{ "Skill_Name": { "description": "...", "types": ["Passive"], "range": "Melee", "mods": [], "payloads": [] } }
```