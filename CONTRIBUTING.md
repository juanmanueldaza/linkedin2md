# Contributing to linkedin2md

Thanks for your interest! Here's how to set up your dev environment and contribute.

## N3RV (AI Agent Infrastructure)

This project uses [N3RV](https://github.com/juanmanueldaza/n3rv) for agent-native development — Spec-Driven Development (SDD) workflow, A2A agent hub, persistent memory, and OpenCode integration.

```bash
# Install N3RV
git clone https://github.com/juanmanueldaza/n3rv.git ~/n3rv
cd ~/n3rv && uv tool install .

# Initialize in this project
cd /path/to/linkedin2md
n3rv init
```

See `.opencode/agents/n3rv.md` for available commands, skills, and SDD agents.

## Development Setup

```bash
# Clone the repo
git clone https://github.com/juanmanueldaza/linkedin2md.git
cd linkedin2md

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Lint and type check
ruff check .
ruff format --check .
pyright
```

## Making Changes

1. Create a branch: `git checkout -b my-feature`
2. Make your changes
3. Ensure all tests pass: `pytest -v`
4. Ensure linting passes: `ruff check . && ruff format --check .`
5. Ensure type checking passes: `pyright`
6. Commit with a descriptive message (see commit conventions below)
7. Push and open a Pull Request

## Commit Conventions

- Use conventional commit format: `type: description`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`
- Reference issue numbers: `fix #2`, `closes #5`
- Keep commits focused — one logical change per commit

## Code Style

- **Formatter**: ruff (line length 88, target Python 3.13+)
- **Type checker**: pyright (strict mode)
- **Linting**: ruff check with rules E, W, F, I, B, UP
- **Type annotations**: required on all public function signatures
- **Zero-dependency core**: only Python stdlib in the main package

## Testing

- **Framework**: pytest
- **Test location**: `tests/` directory, files named `test_*.py`
- **Test classes**: group related tests in `class TestXxx` with descriptive docstrings
- **Edge cases**: test empty inputs, None, unicode, special characters
- **Security tests**: path traversal, URL sanitization, file size limits

## Good First Issues

Look for issues tagged [good first issue](https://github.com/juanmanueldaza/linkedin2md/labels/good%20first%20issue) — these are specifically chosen to be approachable for new contributors.

## Questions?

Open an issue or start a discussion at [github.com/juanmanueldaza/linkedin2md/discussions](https://github.com/juanmanueldaza/linkedin2md/discussions).