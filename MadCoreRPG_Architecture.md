# MadCore RPG Master Architecture & Design Document

## 1. Core Philosophy and Architecture

The MadCore RPG architecture is a strictly data-driven engine separated into three distinct layers:

* **Definitions (The Blueprints):** Static blueprints defining what a stat is.
* **Entity (The Container):** The living object that holds dictionaries of initialized stats and processes event queues.
* **Effect Payloads (The Operations):** Packaged instructions that are sent to Entities to trigger state changes.

## 2. Core Enumerations (The Engine Rules)

The engine relies on strictly defined enumerations to govern how math and states are processed.

### StatType

Defines the fundamental nature of a stat.

* `Raw`: A basic attribute that is an unmodified value.
* `Potential`: A derived stat that calculates a maximum ceiling based on formulas.

### ModifierType

Defines how a continuous modifier interacts with a stat's mathematical pipeline.

* `Flat`: Adds a constant numerical value directly to the stat.
* `Percentage`: Multiplies the stat by a percentage value.
* `Override`: Completely replaces the stat's value with the provided number, ignoring previous math.

### StatModificationType

Defines how an incoming effect alters a stat.

* `Flat`: Instantly adjusts the current value (or base value).
* `Percentage`: Instantly adjusts the current value by a percentage.
* `Override`: Instantly overwrites the current value.
* `StatModifier`: Attaches a persistent `StatModifier` object to the stat's modifier list.

### EffectType

Categorizes the broad purpose of an Effect Payload.

* `StatModification`: Modifies the core values of stats.
* `StatModifier`: Applies active, continuous modifiers.
* `Other`: Used for custom triggers or non-stat events.

## 3. Data Structures & Mandatory Fields

### The Stat Definition (Blueprint)

Every stat in the game must originate from a `StatDefinition` object.

* **Mandatory Fields:**
* `id` (String): The absolute unique identifier used by the engine to target the stat.
* `displayName` (String): The human-readable name for UI purposes.
* `description` (String): The UI-friendly text explaining the stat.
* `spriteIcon` (String): The file path or reference for the stat's visual icon.
* `baseValue` (Float): The default starting value of the stat.
* `statType` (`StatType`): Must be assigned as either `Raw` or `Potential`.



### Stat Modifiers

A continuous buff or debuff attached to a stat.

* **Mandatory Fields:**
* `type` (`ModifierType`): Determines if the modifier is Flat, Percentage, or Override.
* `value` (Float): The mathematical weight of the modifier.
* `source` (String): Tracks where the modifier came from (e.g., "Iron Boots") to allow for easy removal.
* `statId` (String): The ID of the stat this modifier belongs to.



### Effect Payloads

The sole method for interacting with an Entity's state. Entities do not take damage; they receive Effect Payloads.

* **Mandatory/Core Fields:**
* `EffectId` (String): Unique identifier, usually generated automatically as a GUID.
* `SourceId` (String): The ID of the Entity or object that caused the effect.
* `EffectType` (`EffectType`): Determines the engine routing for the effect.
* `StatModifications` (List of `StatModificationData`): An array containing the specific mathematical instructions.
* `IsIndefinite` (Boolean): If true, the effect lasts until manually removed.
* `Lifetime` (Float): The time duration before the effect naturally expires.
* `CanBeRemoved` (Boolean): Determines if the effect can be purged by other systems.



### Stat Modification Data

The instructions nested inside an Effect Payload.

* **Mandatory Fields:**
* `StatId` (String): The specific stat to alter.
* `Value` (Float): The mathematical value of the alteration.
* `ModificationType` (`StatModificationType`): How the value is applied (e.g., Flat instant change vs attaching a modifier).
* `Modifier` (`StatModifier`): Must be provided if the `ModificationType` is set to `StatModifier`.



## 4. The Stat Ecosystem

### Raw Stats

Represent fundamental, fixed attributes.

* They inherit from the base `Stat` class and set their `StatType` to `Raw` during initialization.
* When a direct modification payload targets a `RawStat`, the engine permanently alters the `baseValue` of its internal `StatDefinition`.

### Potential Stats

Represent dynamic pools or derived values.

* They inherit from the base `Stat` class and set their `StatType` to `Potential`.
* **Additional Properties:** They hold a `calculationFormula` string, a `maxValue` float, and a `currentValue` float.
* **Clamping:** The `currentValue` is strictly clamped; it cannot drop below zero, nor can it exceed the `maxValue`.
* **Adjustments:** Direct modification payloads target the `currentValue` (e.g., taking damage), while `maxValue` changes happen automatically via the formula.

## 5. The Math Engine Pipeline

### Standard Value Calculation

When the engine requests `GetCurrentValue()` from any stat, it runs a strict, unchangeable pipeline.

1. **Base:** The calculation starts with the `baseValue` from the stat's definition.
2. **Flat Addition:** The engine sums the `value` of all modifiers whose type is `Flat`, and adds this to the base.
3. **Percentage Multiplication:** The engine iterates through all `Percentage` modifiers, calculating a cumulative multiplier using `(1 + modifier.value)`. The post-flat total is multiplied by this final multiplier.
4. **Override:** If any modifier of type `Override` exists in the list, its value completely replaces the results of steps 1-3.

### The Formula Parser

Potential Stats calculate their `maxValue` dynamically using the `StatFormulaParser`.

* **Capabilities:** The parser handles standard arithmetic operators (`+`, `-`, `*`, `/`) and recursive parentheses.
* **Stat Referencing:** If a term in the formula string matches a valid stat ID in the Entity's dictionary, the parser fetches that stat's `GetCurrentValue()` to use in the math.
* **Functions:** The parser supports explicit mathematical functions, specifically `Max(x, y)` and `Min(x, y)`.
* **Failsafes:** The parser includes strict error handling to catch divide-by-zero exceptions and returns 0f if the formula fails to evaluate.

## 6. The Entity Container & Lifecycle

The `Entity` class is the host environment for all systems.

### Core Architecture

* An entity is defined by a string `id`, a string `iconPath`, and an `allStats` dictionary that maps string IDs to instantiated `Stat` objects.
* It implements `IStatChangeEvent` to broadcast system-wide notifications when any stat changes, providing the old and new values.

### Effect Processing Queue

* To prevent race conditions, when an Entity receives an effect via `ApplyEffect`, it places it into an `effectPayloadQueue`.
* The entity locks processing using a boolean (`isProcessingEffects`) and dequeues payloads one by one.
* For each payload, the Entity iterates through its `StatModifications` array.
* If a `RawStat` is modified, the Entity triggers `UpdateCalculatedMutableMaxStats()`, forcing every `PotentialStat` in its dictionary to recalculate its max value via the parser.
* Effects that are not flagged as `IsIndefinite` are saved into an `activeEffects` list so they can be tracked and eventually reverted via `RemoveEffect`.