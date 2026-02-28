# Eco Crafting Calculator

A browser-based crafting cost calculator for the game [Eco](https://play.eco/). Given a recipe database you build yourself, it recursively calculates the true credit price of any crafted item — accounting for skill levels, crafting table upgrades, lavish workspace talent, byproducts, and server-specific economic settings.

## Features

- **Two-page layout** — ⚡ Pricer for fast lookups, 📖 Recipes for browsing and editing the database
- **Recipe database** — create and manage items with multiple recipe variants per item, including ingredients and byproducts
- **Recursive cost tree** — ingredient costs are calculated at depth, so nested recipes are fully resolved; nodes are collapsible
- **Skill & table modifiers** — configure 33 skills (levels 0–7, lavish workspace) and 67 crafting tables (10 upgrade tiers)
- **Inline Skills & Tables panel** — always visible on the Pricer page; any change immediately recalculates the current result
- **Item tags** — map tag names (e.g. `Wood`) to a group of items whose cost is averaged; view and set tag market prices from the Tags view
- **Issues badge** — flags missing recipes and unpriced raw materials directly in the recipe list
- **Read-only recipe detail view** — click any item to see a summary with recipe tabs, ingredients, byproducts, and a reverse-ingredient lookup ("What uses this?")
- **Calculator** — look up any item, set quantity and profit margin, and get an instant price with a full breakdown
- **Import / Export** — back up or share your recipe database as JSON
- **Data parser** — `parse_eco_data.py` extracts recipe, skill, table, and tag data directly from Eco's game files
- **No install required** — single HTML file, runs entirely in the browser with no build step

## Usage

The app fetches its data from local JSON files, so it must be served over HTTP — opening `index.html` directly as a `file://` URL will not work.

Serve the `public/` folder with any static HTTP server:

```bash
# Python (built-in, no install needed)
python -m http.server 8080
# then open http://localhost:8080/public/
```

```bash
# Node http-server
npx http-server public -p 8080 -o
```

Or use the VS Code **Live Server** extension — right-click `public/index.html` → *Open with Live Server*.

## Updating Recipe Data

When Eco patches change recipes, skills, or crafting tables, run the data parser to regenerate the JSON files:

```bash
python parse_eco_data.py
```

This reads from Eco's AutoGen source files at:
```
C:\Program Files (x86)\Steam\steamapps\common\Eco\Eco_Data\Server\Mods\__core__\AutoGen\
```

After running, click **↺ Reload JSON** in the app header to load the updated data (preserving any market prices and skill levels you have set).

## Development

### Prerequisites

The project uses a VS Code devcontainer (Debian 12 + Node.js LTS). Open in the devcontainer to get all tools configured automatically.

### Commands

```bash
# Format
prettier --write public/index.html

# Lint
htmlhint "**/*.html"
eslint public/index.html
```

### Branching Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable releases only. Each merge is tagged with a version. |
| `develop` | Integration branch for completed features. |
| `feature/<name>` | Individual feature work, branched off `develop`. |

All feature branches are created from and merged back into `develop`. `develop` is merged into `main` at release.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT — see [LICENSE](LICENSE).
