# Eco Crafting Calculator

A browser-based crafting cost calculator for the game [Eco](https://play.eco/). Given a recipe database you build yourself, it recursively calculates the true credit price of any crafted item — accounting for skill levels, crafting table upgrades, lavish workspace talent, byproducts, and server-specific economic settings.

## Features

- **Recipe database** — create and manage items with multiple recipes per item, including ingredients and byproducts
- **Recursive cost tree** — ingredient costs are calculated at depth, so nested recipes are fully resolved
- **Skill & table modifiers** — configure 24 skills (levels 0–7, lavish workspace) and 32 crafting tables (10 upgrade tiers)
- **Item tags** — map tag names (e.g. `Wood`) to a group of items whose cost is averaged
- **Calculator** — look up any item, set quantity and profit margin, and get an instant price with a full breakdown
- **Import / Export** — back up or share your recipe database as JSON
- **No install required** — single HTML file, runs entirely in the browser with no server or build step

## Usage

Open `eco-price-calc.html` directly in a browser. No installation or internet connection required.

For local development with live reload, use the VS Code Live Server extension (right-click the file → *Open with Live Server*) or run:

```bash
http-server -p 8080 -o
```

## Development

### Prerequisites

The project uses a VS Code devcontainer (Debian 12 + Node.js LTS). Open in the devcontainer to get all tools configured automatically.

### Commands

```bash
# Format
prettier --write eco-price-calc.html

# Lint
htmlhint "**/*.html"
eslint eco-price-calc.html
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
