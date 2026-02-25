# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

## [1.0.0] - 2026-02-26

### Added

- `recipes.json`, `skills.json`, `tables.json`, `item-tags.json` — default data extracted from the app into standalone files for easier patching
- App fetches the four JSON files in parallel on first run to seed localStorage, with a brief "Loading defaults…" indicator
- Hardcoded defaults remain as offline fallback if any fetch fails
- Recipe database with create, edit, and delete support
- Multiple recipes per item with configurable default
- Ingredients and byproducts per recipe, with reducible flag
- Recursive cost tree calculation resolving nested recipes
- Skill modifier system — 24 skills, levels 0–7, lavish workspace talent
- Crafting table upgrade system — 32 tables, 10 upgrade tiers
- Item tag support — map tag names to groups of items with averaged cost
- Calculator with quantity input, profit margin, and full cost breakdown
- Global calculator settings: credits-per-calorie rate, currency symbol, craft resource modifier
- Per-recipe profit margin override
- Import and export of recipe database as JSON
- Search and autocomplete in both the recipe list and calculator
- Recipe list grouping by name, type, skill, or crafting table
- Resizable three-panel layout
- Dark theme UI
- Embedded help documentation

[Unreleased]: https://github.com/sam-bealmer/Eco-Crafting-Calculator/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/sam-bealmer/Eco-Crafting-Calculator/releases/tag/v1.0.0
