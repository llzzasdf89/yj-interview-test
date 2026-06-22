#!/usr/bin/env bash
set -euo pipefail

# ─── Colours ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

# ─── Dependency checks ────────────────────────────────────────────────────────
command -v uv  >/dev/null 2>&1 || error "uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
command -v npm >/dev/null 2>&1 || error "npm not found. Install Node.js from https://nodejs.org"

# ─── Python version check (requires 3.10+) ───────────────────────────────────
PYTHON_BIN=$(command -v python3 || command -v python || true)
[ -z "$PYTHON_BIN" ] && error "Python not found. Install Python 3.10+ from https://python.org"

PY_MAJOR=$("$PYTHON_BIN" -c "import sys; print(sys.version_info.major)")
PY_MINOR=$("$PYTHON_BIN" -c "import sys; print(sys.version_info.minor)")
PY_VERSION="${PY_MAJOR}.${PY_MINOR}"

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
  error "Python 3.10+ required (found ${PY_VERSION}). Please upgrade: https://python.org"
fi
success "Python ${PY_VERSION} detected."

# ─── Backend setup ────────────────────────────────────────────────────────────
info "Setting up backend..."
cd "$BACKEND"

if [ ! -d ".venv" ]; then
  info "Creating virtual environment with uv..."
  uv venv .venv
fi

info "Installing Python dependencies..."
uv pip install -r requirements.txt --quiet

success "Backend dependencies ready."

# ─── Frontend setup ───────────────────────────────────────────────────────────
info "Setting up frontend..."
cd "$FRONTEND"

if [ ! -d "node_modules" ]; then
  info "Installing npm dependencies..."
  npm install --silent
fi

success "Frontend dependencies ready."

# ─── Cleanup on exit ─────────────────────────────────────────────────────────
cleanup() {
  echo ""
  info "Shutting down..."
  [ -n "${BACKEND_PID:-}" ] && kill "$BACKEND_PID" 2>/dev/null && success "Backend stopped."
  [ -n "${FRONTEND_PID:-}" ] && kill "$FRONTEND_PID" 2>/dev/null && success "Frontend stopped."
  exit 0
}
trap cleanup SIGINT SIGTERM

# ─── Start backend ────────────────────────────────────────────────────────────
info "Starting backend on http://localhost:8000 ..."
cd "$BACKEND"
uv run uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
sleep 2   # give uvicorn a moment to bind

# ─── Start frontend ───────────────────────────────────────────────────────────
info "Starting frontend on http://localhost:3000 ..."
cd "$FRONTEND"
npm run dev &
FRONTEND_PID=$!

# ─── Ready ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  App is running!${NC}"
echo -e "  Frontend  →  ${CYAN}http://localhost:3000${NC}"
echo -e "  Swagger   →  ${CYAN}http://localhost:8000/docs${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  Press ${YELLOW}Ctrl+C${NC} to stop both services."
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
