# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-02-28

### Added

- Two-page layout: ⚡ Pricer and 📖 Recipes tabs in the header; last viewed page is remembered
- Skills & Tables panel now always visible as a side panel on the Pricer page (previously a modal)
- Auto-recalc when skill level, lavish setting, or table upgrade is changed on the Pricer page
- "↺ Reload JSON" button to reload recipes, skills, tables, and item-tags from JSON files without clearing market prices or skill levels
- Collapsible ingredient cost tree — click any parent node to collapse/expand its subtree; Ctrl+click to collapse/expand the entire tree
- Recipe detail read-only view — clicking an item in the recipe list now shows a summary view with recipe tabs, ingredient tables, byproducts, and a "What uses this?" reverse-ingredient lookup
- "⚡ Price It" button in recipe detail view — switches to the Pricer page and calculates cost using the currently viewed recipe tab
- "✎ Edit" button in recipe detail view to enter the edit form
- Issues badge (⚠ N issues) in the recipe list header — click to filter to items with missing recipes or unpriced raw materials
- Items / Tags toggle in the recipe list left panel — Tags view lists all item tag groups with member counts and market prices
- Tag detail panel showing all member items (each clickable to navigate to that item's recipe) and a market price input for the tag group

### Changed

- Recipe list defaults to read-only detail view instead of opening the edit form directly
- Settings modal removed; Skills & Tables are now inline on the Pricer page
- "Tool" item tag included in `item-tags.json` (previously excluded from the data parser); contains 46 tool items
- All localStorage keys bumped — existing saved data from v1.x will not be loaded; use the Reload JSON button to re-seed from the data files

### Fixed

- JSON data files were only fetched on the very first visit; returning visitors always saw stale localStorage data — resolved by the Reload JSON button
- Clear error message shown when the app is opened via `file://` protocol (browsers block `fetch()` in that context; app now instructs user to serve via HTTP)
- Issues filter showed no results for missing-recipe items because those items do not exist in the database — fixed with a dedicated rendering path

### Removed

- Backwards compatibility with v1.x localStorage storage formats (`eco_recipe_db_v2`, `eco_recipe_db_v3`, `eco_skills_v3`, `eco_tables_v2`, `eco_item_tags_v1`, `eco_calc_settings_v1`)
- `laborCalories` field alias in recipe data — use `laborPoints` only

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

[Unreleased]: https://github.com/sam-bealmer/Eco-Crafting-Calculator/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/sam-bealmer/Eco-Crafting-Calculator/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/sam-bealmer/Eco-Crafting-Calculator/releases/tag/v1.1.0
[1.0.0]: https://github.com/sam-bealmer/Eco-Crafting-Calculator/releases/tag/v1.0.0
