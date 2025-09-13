# Common Contributions

Most community PRs fall into two buckets:

1. **SQLModels**: adding/updating table models for the Civ VII databases.
2. **Bindings**: extending the Python → JavaScript runtime adapters (via Transcrypt) for the in-game API.

---

## Adding new SQLModels

This section shows how to discover unimplemented tables, inspect their schemas, and add corresponding `SQLModel` classes.

### 1. Find Unimplemented Tables

Run the scan script:

```bash
uv run --script scripts/scan_incomplete_tables.py
```

!!! info
    The script launches Civ VII in **debug** mode. In debug mode, Civ VII writes *copy* databases into your settings directory:

    ```pgsql
    <SettingsDir>/
      └─ Debug/
          ├─ colors-copy.sqlite
          ├─ frontend-copy.sqlite
          ├─ gameplay-copy.sqlite
          ├─ images-copy.sqlite
          └─ localization-copy.sqlite
    ```

After you **exit the game**, the script inspects those files and prints all tables that don't yet have models in **pyciv7**.

### 2. Inspect the Table Schema

Open the relevant `*-copy.sqlite` in any SQLite viewer (DB Browser for SQLite, VS Code's SQLite extension, etc.) and copy the `CREATE TABLE` statement for the SQLModel you plan to implement.

!!! tip
    To get to your Civ VII settings directory containing the SQLite dumps, you can print your settings path with:

    ```bash
    uv run python -c "from pyciv7.settings import Settings; print(Settings().civ7_settings_dir)"
    ```
<image>

### 3. Create the SQLModel

Use the `CREATE TABLE` as the source of truth and map each column to a typed field.

```python
# Example from image
```

!!! tip "Mapping Tips"
    - `TEXT → str`, `INTEGER → int`, `REAL → float`, `BOOLEAN → bool`
    - Primary keys → `Field(primary_key=True)`
    - Autoincrement (integer PK) → `Optional[int] = Field(default=None, primary_key=True)`
    - Foriegn keys → `Field(foriegn_key="OtherTable.OtherColumn")`
    - Keep **exact** table and column names to match game schema

## Adding new API Bindings

TODO: more description here

To locate
