# Understanding the code (without losing your mind)

You're curious about how GamePilot is built. You're not a full-time developer. Cool. This doc is a friendly tour, not a textbook.

## The 30-second mental model

GamePilot has three pieces:

1. **Backend** (Python). The brains. Watches the screen, decides what to do, presses keys. Lives in `gamepilot/`.
2. **Frontend** (HTML + CSS + a little JavaScript). The pretty interface in your browser. Lives in `frontend/`.
3. **Glue** (Makefile + scripts). The "make install / start / stop" wrapper. Lives in `Makefile` + `scripts/`.

When you run `make start`, the glue boots the backend, which serves the frontend, which talks back to the backend. Done.

## Folder tour

```
GamePilot/
├── frontend/                   ← what you see in the browser
│   ├── landing.html              · marketing page (the / route)
│   ├── app.html                  · the actual UI (the /app route)
│   ├── colors_and_type.css       · design tokens (palette, fonts)
│   ├── api.js                    · talks to the backend
│   └── logo-*.svg                · brand marks
│
├── gamepilot/                  ← the Python package (the brain)
│   ├── app/api/                  · the web server (FastAPI)
│   │   ├── server.py             · main routes (/health, /command, /news, …)
│   │   └── frontend_compat.py    · legacy /api/* routes for the old dashboard
│   ├── app/discover/             · top-played Steam games + compat tiers
│   ├── app/perception/           · "look at the screen" code
│   ├── app/decision/             · "decide what to do" code
│   ├── app/executor/             · "press a key" code
│   └── app/safety/               · time caps, emergency stop, multiplayer block
│
├── docs/                       ← the docs you're reading right now
├── tests/                      ← automated tests
├── scripts/
│   └── bootstrap.py              · cross-platform install / start / stop helper
├── Makefile                    ← shortcut wrapper (make install / start / stop)
└── pyproject.toml              ← Python dependencies
```

## How a click flows through the system

Let's trace one: you click **"Engage Autopilot"** in the dashboard.

1. **`frontend/app.html`** has the button: `<button class="btn btn-engage">Engage Autopilot</button>`.
2. **`frontend/api.js`** notices the click in `bindEngage()`. The text "Engage Autopilot" matches a known intent → it calls `api.command('beat boss')`.
3. **`api.js`** makes an HTTP POST to `/command` with `{"text": "beat boss"}`.
4. **`gamepilot/app/api/server.py`** has a route for `/command`. It calls `parse_command()`, which sets `blackboard.current_goal = "beat_boss"`.
5. The response comes back. `api.js` shows a "command sent" line in the chat log. `refresh()` polls `/state` to update the UI.

That's the whole loop. **No magic. No hidden layers.**

If you want to change what "Engage Autopilot" does, you edit either:

- `frontend/api.js` (intent matcher) — for "what command should this button send?"
- `gamepilot/app/commands.py` — for "what does the backend do when it gets that command?"

## "What's FastAPI / uvicorn / pydantic?"

In gamer terms:

- **FastAPI** = the framework that turns Python functions into web routes. `@app.get("/health")` above a function means "when someone hits `/health`, run this function." That's it.
- **uvicorn** = the actual web server that runs FastAPI. Like the engine running the framework.
- **pydantic** = the thing that validates incoming JSON. If a route expects `{"text": str}` and you send `{"text": 42}`, pydantic catches it and returns a 422 error before your code runs. Saves headaches.

Together they're the standard Python web stack. Nothing weird.

## "What's a venv? What's uv?"

- **venv** = "virtual environment." A folder (`.venv/`) that holds an isolated copy of Python and all its packages. Keeps GamePilot's libraries from fighting with anything else on your computer. Made automatically by `make install`.
- **uv** = a fast Python package manager. Like `pip`, but 10x faster and friendlier on Windows. We use it because the alternative (`pip` + `venv` + `pip-tools`) is three tools where uv is one.

You don't have to know these to use GamePilot. You only meet them if you're poking inside.

## The "blackboard"

`gamepilot/app/blackboard.py` defines a single shared object that holds the current state:

```python
@dataclass
class Blackboard:
    current_goal: str = "explore"
    last_action: str = "idle"
    emergency_stop: bool = False
    # …
```

Anything that needs to know "what should the AI do right now?" reads it. Anything that wants to change behaviour writes to it. **It's a tiny in-memory database.** That's the whole magic.

In v0.2 this'll move to a proper persistent store. For now, simple wins.

## Where the AI actually lives

Three folders, three jobs:

- **`gamepilot/app/perception/`** — "what's on screen right now?" Takes pixels in, returns a structured state (HP %, enemy nearby, scene type, etc).
- **`gamepilot/app/decision/`** — "given that state, what should we do?" Takes state in, returns an action label ("dodge_right", "attack_heavy", etc).
- **`gamepilot/app/executor/`** — "press the keys for that action." Takes action label in, presses real keys via `pynput`.

Run them in a loop, you've got autopilot. Each piece is small and replaceable — that's the design.

## The frontend in 60 seconds

The whole UI is **one HTML file** (`app.html`) plus **one CSS file** (`colors_and_type.css`) plus **one JS file** (`api.js`).

No React. No Vue. No build step. Open `app.html` in a browser and it works. We picked this because:

- It's auditable. You can read every line.
- It loads instantly.
- It survives forever — no framework deprecations.

The "screens" (Dashboard, Autopilot, Coach, Safety, Models, News) are all `<div class="screen">` blocks in the same file, toggled by `display:` CSS based on which sidebar item you clicked. **It's one page that hides and shows sections.**

If you want to tweak a screen, search `app.html` for the screen name and you'll find the markup. Mess with it — it'll hot-reload if you edit while `make start` is running.

## Where to start poking

Want to feel productive? Try these:

1. Add a quick-chip to the AI Coach. Search `app.html` for `class="quick"`, copy a line, change the text.
2. Add a game to `gamepilot/app/discover/compatibility_index.json`. The schema is obvious from the existing entries.
3. Tweak the brand colours in `frontend/colors_and_type.css`. Re-load the page — instant feedback.
4. Read `tests/test_frontend_compat_api.py`. It's short and shows how the routes are exercised.

Each of those is a 5-minute change, no expertise required. **That's the win.**

## Reading more

- [docs/AUTOPILOT_GUIDE.md](AUTOPILOT_GUIDE.md) — deeper on how autopilot decision-making works.
- [docs/ARCHITECTURE.md](ARCHITECTURE.md) — the official high-level design doc.
- [docs/model_contract.md](model_contract.md) — what a model file has to look like to be loadable.

If those feel too dense, that's fine. You don't need them to use or contribute. Come back when you do.
