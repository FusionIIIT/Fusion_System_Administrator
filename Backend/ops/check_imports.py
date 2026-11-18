"""Import every module of the backend, so code that cannot even load fails here.

`manage.py check` loads models, URLs and views, but not management commands or
tests, and a module can compile and still fail the moment it loads (a type
written for a newer Python, for instance). The server runs Python 3.8; CI runs
this on 3.8, and the deploy script runs it with the server's own virtualenv
before restarting anything.

Run from Backend/backend:  python ../ops/check_imports.py
Uses DJANGO_SETTINGS_MODULE when set, backend.settings otherwise.
"""
import importlib
import os
import sys

import django

SKIP_DIRS = {"__pycache__", "migrations", "node_modules", "venv"}
# One-off data scripts that need pandas, which the service does not install.
SKIP_MODULES = {"add_professors", "update_designation_table"}


def module_names(root):
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.endswith(".py") or name == "manage.py":
                continue
            path = os.path.relpath(os.path.join(folder, name), root)[:-3]
            module = path.replace(os.sep, ".")
            if module.endswith(".__init__"):
                module = module[: -len(".__init__")]
            if module and module not in SKIP_MODULES:
                yield module


def main():
    root = os.getcwd()
    sys.path.insert(0, root)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
    django.setup()
    failed = 0
    names = list(module_names(root))
    for module in names:
        try:
            importlib.import_module(module)
        except Exception as error:  # report every module that fails, then stop
            failed += 1
            print(f"FAILED {module}: {type(error).__name__}: {error}")
    print(f"Python {sys.version.split()[0]}: imported {len(names) - failed} of {len(names)} modules")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
