#!/bin/bash
set -e

echo "Setting up Eco Price Calc HTML development environment..."


# ── Node.js (installed via devcontainer feature) ──────────────────────────────
echo "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed!"
    exit 1
fi
echo "  node:  $(node --version)"
echo "  npm:   $(npm --version)"

# ── Global npm tools ──────────────────────────────────────────────────────────
echo "Installing global npm tools..."

# Prettier — HTML/CSS/JS formatter
if ! command -v prettier &> /dev/null; then
    npm install -g prettier
else
    echo "  prettier already installed, skipping"
fi

# HTMLHint — HTML static analysis
if ! command -v htmlhint &> /dev/null; then
    npm install -g htmlhint
else
    echo "  htmlhint already installed, skipping"
fi

# ESLint — JavaScript linter
if ! command -v eslint &> /dev/null; then
    npm install -g eslint
else
    echo "  eslint already installed, skipping"
fi

# http-server — lightweight static file server (useful outside Live Server)
if ! command -v http-server &> /dev/null; then
    npm install -g http-server
else
    echo "  http-server already installed, skipping"
fi

# ── Prettier config (if not already present) ──────────────────────────────────
WORKSPACE_DIR="/workspaces/${WORKSPACE_FOLDER_BASENAME:-$(basename "$(pwd)")}"
PRETTIER_CONFIG="${WORKSPACE_DIR}/.prettierrc"
if [ ! -f "${PRETTIER_CONFIG}" ]; then
    echo "Writing default .prettierrc..."
    cat > "${PRETTIER_CONFIG}" << 'PRETTIEREOF'
{
  "printWidth": 120,
  "tabWidth": 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": false,
  "trailingComma": "es5",
  "bracketSameLine": true
}
PRETTIEREOF
fi

# ── Claude CLI ────────────────────────────────────────────────────────────────
if ! command -v claude &> /dev/null; then
    echo "Installing Claude CLI..."
    curl -fsSL https://claude.ai/install.sh | bash
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "  claude already installed, skipping"
fi

# ── Git safe directory ────────────────────────────────────────────────────────
git config --global --unset-all safe.directory || true
git config --global --add safe.directory '*'

# ── Bash aliases ──────────────────────────────────────────────────────────────
cat >> ~/.bashrc << 'EOF'

# Eco Price Calc — HTML Dev Aliases
alias gs='git status'
alias gd='git diff'
alias gl='git log --oneline --graph --decorate -20'

# Serve the current directory on port 8080
alias serve='http-server -p 8080 -o'

# Format all HTML/CSS/JS files in the workspace
alias format-all='prettier --write "**/*.{html,css,js,json}" --ignore-path .gitignore 2>/dev/null || prettier --write "**/*.{html,css,js,json}"'

# Lint HTML files
alias lint-html='htmlhint "**/*.html"'

EOF

echo ""
echo "=== Environment ready! ==="
echo "Tools installed:"
echo "  - Node.js:      $(node --version)"
echo "  - npm:          $(npm --version)"
echo "  - prettier:     $(prettier --version)"
echo "  - htmlhint:     $(htmlhint --version)"
echo "  - eslint:       $(eslint --version)"
echo "  - http-server:  $(http-server --version 2>&1 | head -n1)"
echo "  - claude:       $(claude --version 2>&1 || echo 'not in PATH yet')"
echo ""
echo "Useful commands:"
echo "  serve           — start http-server on port 8080"
echo "  format-all      — prettier-format all HTML/CSS/JS files"
echo "  lint-html       — run HTMLHint on all HTML files"
echo "  Live Server     — right-click any .html file in VS Code → 'Open with Live Server'"
