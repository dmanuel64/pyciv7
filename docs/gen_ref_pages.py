"""
Generate the code documentation pages and navigation.
"""

import mkdocs_gen_files

from pathlib import Path
from mkdocs_gen_files.nav import Nav

nav = Nav()

# Get all python source code files
for path in sorted(p for p in Path("src").rglob("*.py") if 'resources' not in p.parts):
    # Get module and docs paths
    module_path = path.relative_to("src").with_suffix("")
    doc_path = path.relative_to("src").with_suffix(".md")
    full_doc_path = Path("documentation", doc_path)

    parts = tuple(module_path.parts)

    # Remove __init__ from module parts and skip __main__
    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    nav[parts] = doc_path.as_posix()

    # Add to mkdocs page
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"::: {ident}")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

# Create navigation file
with mkdocs_gen_files.open("documentation/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
