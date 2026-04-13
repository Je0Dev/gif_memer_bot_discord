# Contributing to Meme Bot Dashboard

Thank you for your interest in contributing!

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Install dev dependencies: `pip install -r requirements.txt[dev]`
5. Copy `.env.example` to `.env` and fill in your credentials
6. Run pre-commit install: `pre-commit install`

## Running the Bot

```bash
python main.py
```

## Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=cogs --cov=main
```

## Code Style

We use several tools to maintain code quality:

- **Black** - Code formatting
- **isort** - Import sorting
- **Ruff** - Linting
- **Mypy** - Type checking

Run them all with:
```bash
pre-commit run --all-files
```

Or install pre-commit hooks to run automatically:
```bash
pre-commit install
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Ensure tests pass: `pytest`
5. Run linting: `ruff check . && mypy .`
6. Commit your changes using conventional commits
7. Push to your fork
8. Open a Pull Request

## Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(memes): add trending GIF command

Add /trending command to fetch trending GIFs from configured providers.
Includes automatic fallback to secondary provider.
```

## Reporting Issues

Please include:
- Discord bot version
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs

## Questions?

Open an issue for discussion before making significant changes.
