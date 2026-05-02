# If something breaks

Don't panic. Read the symptom, do the fix. If your symptom isn't here, [open an issue](https://github.com/ruslanmv/GamePilot/issues/new) — paste the error message, we'll add it.

---

## During install

### `'make' is not recognized as an internal or external command`

You're on Windows and `make` isn't installed.

**Fix:** Two options:

1. Install Chocolatey, then in an admin PowerShell: `choco install make`
2. Or skip `make` entirely. Run the same steps directly:
   ```
   python scripts/bootstrap.py install-uv
   python scripts/bootstrap.py ensure-deps
   python scripts/bootstrap.py start
   ```

### `Python not found` / `python: command not found`

Python isn't installed, or it's not on your PATH.

**Fix:** Reinstall from [python.org/downloads](https://www.python.org/downloads/), and on Windows **tick "Add python.exe to PATH"** during install. Reopen your terminal afterwards.

### `-v was unexpected at this time`

You're on Windows. This is fixed in the latest code — pull and retry:

```
git pull
make install
```

### `Failed to create virtual environment / lib64: Access is denied`

A previous run left a half-broken `.venv`. Latest code auto-handles this; if you're on an older version:

```
make stop
rmdir /s /q .venv     (Windows)
rm -rf .venv          (macOS / Linux)
make install
```

### `make install` runs forever

It's not stuck. The first install downloads ~150 MB of Python packages. Allow 3–5 minutes on a normal connection. Look for `Installation complete.` at the end.

If it actually hangs (no progress for 5+ min): Ctrl+C, then:

```
make clean-all
make install
```

---

## During `make start`

### `http://localhost:8000/` shows `{"detail":"Not Found"}`

The server is running but can't find the frontend folder.

**Fix:** Make sure you're running `make start` from inside the GamePilot folder (where `Makefile` lives). If you are, pull the latest — this was a Windows-specific bug fixed in commit `11e3846`.

### Browser opens to "This site can't be reached"

The server didn't actually start.

**Fix:** Check the log:

```
type logs\gamepilot-server.log     (Windows)
cat logs/gamepilot-server.log      (macOS / Linux)
```

If it says "address already in use" — see "Port 8000 is busy" below.
If it says anything about `ImportError` or `ModuleNotFoundError` — re-run `make install`.

### Port 8000 is busy

Something else is using port 8000.

**Fix:** Either close that other thing, or run on a different port:

```
make stop
make start PORT=8765
```

Then open `http://localhost:8765/app`.

### A black cmd window flashes and disappears

Old behaviour. Fixed in latest. `git pull` and re-run `make start`.

### Browser doesn't auto-open

Sometimes the OS doesn't honor the auto-open. The server is fine — just open the URL manually:

```
http://localhost:8000/app
```

### `make start` says "GamePilot is up" but the page is blank

Hard-refresh the browser (`Ctrl+Shift+R` / `Cmd+Shift+R`). If still blank, check the browser's dev console (F12) for red errors and paste them in a GitHub issue.

---

## During use

### News tab shows `Steam charts unreachable`

Steam's API is down or your network is blocking it. **GamePilot will show cached results** with an age stamp. Click **Refresh** to retry. If it persists 10+ min, it's Steam's side, not ours.

### News tab numbers all show "—"

You opened the tab before the first fetch finished. Wait 2 seconds and click Refresh. If they're still all dashes, the Steam fetch failed — check your internet.

### Coach chat doesn't respond

You don't have a Claude / OpenAI / Watsonx key set up yet. The coach needs an LLM provider. For v0.1, that's optional — install the extra:

```
uv pip install gamepilot[companion]
```

And set one of `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `WATSONX_*` in your `.env` file. (We're working on a friendlier setup flow for v0.2.)

### Autopilot button is greyed out

Pre-flight checks failed. Look at the Autopilot setup screen — one of the six rows under "Pre-flight checks" will be red. Common causes:

- Multiplayer detected → exit the lobby.
- Vision model missing → install one from the Models tab.
- Action model missing → install or train one.

### `Ctrl + Shift + Esc` doesn't stop autopilot

This is the most important hotkey. If it's not working:

1. Try clicking the Stop button in the UI.
2. Run `make stop` in a terminal — that nukes the server entirely.
3. As a last resort: close the browser and `make stop`.

If the hotkey itself failed to fire, file a P0 issue with your OS and game name. That's a bug we treat as critical.

---

## Generic recovery: nuke and reinstall

When all else fails:

```
make stop
make clean-all
git pull
make install
make start
```

`clean-all` removes caches and generated data, **but keeps your settings (`.env`) and trained models.** Safe to run.

If even that fails: delete the entire `GamePilot` folder and `git clone` it fresh.

---

## How to file a useful issue

Go to [github.com/ruslanmv/GamePilot/issues/new](https://github.com/ruslanmv/GamePilot/issues/new) and include:

1. **What you were trying to do** ("ran `make start` for the first time").
2. **What happened** ("got error X").
3. **Your OS** (Windows 11 / macOS 14 / Ubuntu 22.04, etc).
4. **The exact error message** — copy-paste, don't paraphrase.
5. **The last 40 lines of `logs/gamepilot-server.log`** if there is one.

Bonus: include `python --version` and `git rev-parse HEAD` (which commit you're on).

We read every issue. Promise.
