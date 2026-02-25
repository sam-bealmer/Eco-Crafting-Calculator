# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-02-25

### Added

- Tag next to title for current Eco Version
- Button to link to source code repository
- Contributing guide in CONTRIBUTING.md
- Pull request template in .github/pull_request_template.md

### Changed

- Replaced "Labor Calories" to "Labor Points". Math remains the same

### Fixed

- Fixed viewport height so "Save Item" button no longer cut off by viewport

## [1.0.0] - 2026-02-25

### Added

- Recipe database with create, edit, and delete support
- Multiple recipes per item with configurable default
- Ingredients and byproducts per recipe, with reducible flag
- Recursive cost tree calculation resolving nested recipes
- Skill modifier system (30 skills, levels 0–7, lavish workspace talent)
- Crafting table upgrade system (35 tables, 10 upgrade tiers)
- Item tag support — map tag names to groups of items with averaged cost
- Calculator with quantity input, profit margin, and full cost breakdown
- Global settings: credits-per-calorie rate, currency symbol, craft resource modifier
- Per-recipe profit margin override
- Import and export of recipe database as JSON
- Search and autocomplete in recipe list and calculator
- Recipe list grouping by name, type, skill, or crafting table
- Resizable three-panel layout with dark theme
- Embedded help documentation
- `recipes.json`, `skills.json`, `tables.json`, `item-tags.json` — default data extracted into standalone files for easier patching between Eco game updates
- App fetches the four JSON files in parallel on first run to seed localStorage; falls back to hardcoded defaults if offline

[Unreleased]: https://github.com/sam-bealmer/Eco-Crafting-Calculator/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/sam-bealmer/Eco-Crafting-Calculator/releases/tag/v1.1.0
[1.0.0]: https://github.com/sam-bealmer/Eco-Crafting-Calculator/releases/tag/v1.0.0
