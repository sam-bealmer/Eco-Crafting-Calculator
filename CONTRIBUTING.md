# Contributing to Eco Crafting Calculator

Thanks for your interest in contributing! This document explains how to get involved.

## Ways to Contribute

- **Bug reports** — open an issue describing what went wrong and how to reproduce it
- **Feature requests** — open an issue describing the use case and what you'd like to see
- **Data updates** — PRs updating `skills.json`, `tables.json`, `recipes.json`, or `item-tags.json` when Eco game updates change recipes, skills, or crafting tables
- **Code changes** — bug fixes or new features via pull request

## Branching Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable releases only. Do not target this in PRs. |
| `develop` | Integration branch. **Target all PRs here.** |
| `feature/<name>` | Your working branch, created from `develop`. |

**Always branch off `develop` and open your PR back into `develop`.** Direct PRs to `main` will not be accepted.

```
develop → feature/my-change (your work)
feature/my-change → develop (your PR)
develop → main (maintainer-only, at release)
```

## Getting Started

1. Fork the repository
2. Create a branch from `develop`:
   ```bash
   git checkout develop
   git checkout -b feature/your-change
   ```
3. Make your changes
4. Run the linters before opening a PR (see below)
5. Open a PR targeting `develop`

## Development Setup

The project uses a VS Code devcontainer (Debian 12 + Node.js LTS). Open the repo in the devcontainer to get all tools configured automatically.

All logic lives in a single file: `public/index.html`. The four JSON files in `public/` are the default data seeded into localStorage on first run.

The app must be served over HTTP to load those JSON files — opening `index.html` directly as a `file://` URL will not work. Use any static file server:

```bash
python -m http.server 8080
# then open http://localhost:8080/public/
```

Or use the VS Code **Live Server** extension.

### Linting and Formatting

Run these before submitting a PR:

```bash
# Format
prettier --write public/index.html

# Lint
htmlhint "**/*.html"
eslint public/index.html
```

PRs with linting errors will be asked to fix them before merging.

## Data Update PRs (Game Updates)

When Eco updates change skills, tables, or recipes, PRs updating the JSON files are especially welcome.

### Using the Data Parser

The easiest way to update the data files is to run `parse_eco_data.py`, which reads directly from Eco's installed game files:

```bash
python parse_eco_data.py
```

This requires Eco to be installed at the default Steam path:
```
C:\Program Files (x86)\Steam\steamapps\common\Eco\Eco_Data\Server\Mods\__core__\AutoGen\
```

The parser preserves any `marketPrice` values already set in the JSON files, so running it will not lose user data.

### Manual Data Updates

If you prefer to edit the JSON files directly:

- `recipes.json` — item recipes; see the schema in the app's Import modal for the expected format
- `skills.json` — skill names (the `level` and `lavish` fields are user-controlled and ignored by the parser)
- `tables.json` — crafting table names (the `upgrade` field is user-controlled)
- `item-tags.json` — tag groups mapping tag names to lists of item names

When submitting a data update PR, please:

- Note the Eco game version the data reflects in your PR description
- Only update the JSON files affected by the patch
- Verify the calculator still produces sensible output after the change

## Commit Messages

Use clear, descriptive commit messages in the imperative mood:

- `Add lavish workspace toggle to skill panel`
- `Fix recursive cost calculation for circular recipes`
- `Update recipes.json for Eco 0.10.x`

## Issues

Before opening an issue, search existing issues to avoid duplicates. When reporting a bug, include:

- What you expected to happen
- What actually happened
- Steps to reproduce
- Browser and OS

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
