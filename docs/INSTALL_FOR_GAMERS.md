# Installing GamePilot (no IT degree required)

Three commands. Two if you're lucky. Read the tiny "before you start" section first.

## Before you start

You need:

- **A PC.** Windows 10/11, macOS, or Linux. We test Windows first because that's where most gamers live.
- **Python 3.11.** If you don't have it, grab the official installer at [python.org/downloads](https://www.python.org/downloads/). On Windows, **tick "Add python.exe to PATH"** during install. This is the one box that matters.
- **`make`.** Comes with macOS / Linux. On Windows: easiest path is install [Chocolatey](https://chocolatey.org/install) then run `choco install make` in an admin PowerShell. Or use **Git Bash** (ships with [Git for Windows](https://git-scm.com/download/win)) — most things work there too.
- **Git.** [git-scm.com/downloads](https://git-scm.com/downloads). Used to grab the code.

That's it. No Docker. No CUDA. No "configure your environment."

## Get the code

Open a terminal (Command Prompt on Windows, Terminal on macOS/Linux), and:

```
git clone https://github.com/ruslanmv/GamePilot.git
cd GamePilot
```

You're now "inside" the project folder. Every command below assumes that.

## The three commands

```
make install
```

Downloads everything GamePilot needs. **First run takes a few minutes** because it pulls Python packages. You'll see a wall of text — that's normal. Done when it says **`Installation complete.`**

```
make start
```

Starts the server in the background. Opens your browser at `http://localhost:8000/app` automatically. You should see the GamePilot interface — dark theme, neon highlights, sidebar on the left.

```
make stop
```

Kills it cleanly when you're done. Don't just close the terminal — use this so the server actually shuts down.

That's the whole loop. `start` → play around → `stop`. Re-run `start` whenever you want to come back.

## "It crashed / it didn't open / the page is broken"

Don't panic. Head to [IF_SOMETHING_BREAKS.md](IF_SOMETHING_BREAKS.md) — every error we've seen so far has a one-line fix.

## Skipping `make` on Windows

If installing `make` is annoying, you can run the same steps directly:

```
python scripts/bootstrap.py install-uv
python scripts/bootstrap.py ensure-deps --python 3.11 --dir .venv
python scripts/bootstrap.py start
```

Same result. `make` is just a friendlier wrapper.

## Updating to a newer version

```
git pull
make install
```

`git pull` grabs the latest code, `make install` re-syncs dependencies if anything changed. You're done.

## Uninstalling

```
make stop
make clean-all
```

Then delete the GamePilot folder. Nothing leaks elsewhere — there's no system-wide install.

(If you want to also free disk: delete `.venv/` inside the project folder. That's where the Python packages live.)

## What "make install" actually does

In plain English, top to bottom:

1. **Installs `uv`** — a fast Python package manager. (Skips if already there.)
2. **Creates a `.venv` folder** — an isolated Python "sandbox" so GamePilot's libraries don't fight with anything else on your computer.
3. **Installs the dependencies** listed in `pyproject.toml`. ~25 small packages, ~150 MB on disk.

It does **not**:

- Modify your system Python.
- Install GPU drivers.
- Touch anything outside the GamePilot folder.

Safe to run as many times as you want. Re-runs are fast (it skips work already done).
