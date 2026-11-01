# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Generic skeleton for a PyQt6 desktop application. Codebase and UI strings are in French.
Meant to be copied/renamed as the starting point for a new PyQt6 project — see
"Personnaliser ce squelette" in [README.md](README.md) for what to rename.

## Commands

```bash
make venv          # create .venv and install requirements.txt + pytest/pytest-qt/pyinstaller
make ui             # regenerate gui/ui_*.py from ui/*.ui via pyuic6 (incremental, only stale ones)
make run            # run the app from source
make test           # run the pytest suite (Qt offscreen, no window appears)
make macos          # build dist/macos/MonApplication.app via PyInstaller
make linux          # cross-build dist/linux/ for Linux from macOS via `container` (Apple's native containerization tool, amd64/Rosetta target)
make linux-native   # build on a real Linux machine/VM (no container)
make dist           # macos + linux, then zip/tar.gz the results into dist/
make clean          # remove build/, dist/, .venv, .venv-linux
```

Run a single test file or test directly with pytest (inside the venv, offscreen platform is required since there's no display in CI/headless environments):

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_main_window.py -v
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_main_window.py::test_name -v
```

`tests/conftest.py` creates the single shared `QApplication` instance required before any
`QWidget`/`QDialog` can be constructed in tests.

## Architecture

- **`ui/*.ui`** — Qt Designer source files (edit these visually for layout changes).
- **`gui/ui_*.py`** — generated from `ui/*.ui` via `pyuic6`; never hand-edit these, regenerate
  instead with `make ui` (a pattern rule regenerates only `.py` files whose `.ui` source is
  newer).
- **`core/`** — application logic. Each window/dialog pairs one generated `Ui_*` class with a
  hand-written class via multiple inheritance (e.g. `class MainWindow(QMainWindow,
  Ui_MainWindow)`), following the pattern in `core/main_window.py`: `setupUi(self)` first, then
  connect widget signals to handler methods. Add new windows/dialogs the same way — one `.ui`
  file in `ui/`, its generated counterpart in `gui/`, one class in `core/`.
- **`main.py`** — entry point; constructs `QApplication`, shows `MainWindow`.
- **`packaging/`** — PyInstaller specs (`macos.spec`, `linux.spec`) and `Dockerfile.linux` used
  by the `make macos`/`make linux` targets. Both specs' `name=` fields and the Makefile's
  `APP_NAME`/`LINUX_BIN` variables must be renamed together when adapting this skeleton.
