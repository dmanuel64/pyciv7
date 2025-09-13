<!-- markdownlint-disable ul-indent -->
# Installation

## Prerequisites

Before installing **pyciv7**, make sure you have:

- Python ≥ 3.9
- A package installer such as [`uv`](https://docs.astral.sh/uv/) (preferred) or `pip`.

!!! warning "Heads-up"
    **pyciv7's** documentation will be using `uv` instead of `pip` for most examples.

- **Sid Meier's Civilization VII** (ideally [via Steam](https://store.steampowered.com/app/1295660/Sid_Meiers_Civilization_VII/)).
    - Optional but recommended: **Sid Meier's Civilization VII Development Tools** (in Steam under Library → Tools). Install these to package/upload mods to the Steam Workshop and to access the official modding documentation.

## Install

Using `uv` (adds to your project's dependencies):

```bash
uv add pyciv7
```

!!! tip
    Alternatively, if your mod can be confined to one Python script, you can create a `uv` script:

    ```bash
    uv init --script <your_mod_script.py>
    uv add --script <your_mod_script.py> pyciv7
    ```

Using `pip` (consider a virtual environment first):

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install pyciv7
```

By default `pyciv7` comes with support for transpiling Python scripts to JavaScript via Transcrypt and handling inline SQL statements.

!!! info "Quick Check"
    Verify the install:

    ```bash
    uv run python -c "import pyciv7; print('pyciv7', pyciv7.__version__)"
    # If installed with pip: python -c "import pyciv7; print('pyciv7', pyciv7.__version__)"
    ```

## Development Install

See the [**Development Guide**](contributing/development-guide.md) for contributor setup (editable install, all extras, dev tools, tests).
