# Contributing to `pyciv7`

Thank you for your interest in contributing to `pyciv7`!

Please feel free to propose a new feature or report a bug.

---

## Development Setup

1. **Fork the repository** and clone your fork:

    ```bash
    git clone https://github.com/your-username/pyciv7.git
    cd pyciv7
    ```

2. **Install all extras and dev dependencies using [`uv`](https://docs.astral.sh/uv/)**:

    ```bash
    uv sync --all-extras --dev
    ```

3. **Run tests** to verify setup:

    ```bash
    uv run pytest
    ```

## Code Style

This project follows **[PEP8](https://peps.python.org/pep-0008/)** and uses [`black`](https://black.readthedocs.io/en/stable/) for auto-formatting. The documentation style is [Google's Python Style](https://google.github.io/styleguide/pyguide.html).

## Commit Guidelines

This project uses conventional commits to automate versioning and changelogs with [`release-please`](https://github.com/googleapis/release-please).

Please use the following prefixes in your commit messages:

- `feat:` — for new features (triggers a **minor** version bump)
- `fix:` — for bug fixes (triggers a **patch** bump)
- `refactor:` — for code improvements (patch bump)
- `chore:` — for maintenance tasks (no version bump)
- `docs:` — for documentation updates (no version bump)
- `test:` — for test-related changes (no version bump)

**Examples:**

- `feat: add function to export model to xml`
- `fix: handle edge case in model serialization`
- `chore: update GitHub Actions workflow`
