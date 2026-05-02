# Using GamePilot

You ran `make start`. The browser opened. Now what?

This is a tour of every screen. Five minutes, top to bottom.

## The two front doors

- **`http://localhost:8000/`** — the marketing landing page. Pretty, but mostly for showing your friends.
- **`http://localhost:8000/app`** — the actual product. **This is where you'll spend your time.**

If you see a glossy hero with "Stop rage quitting. Start winning." — that's the landing. Click around to find the app, or just edit the URL.

## The sidebar (left side of the app)

Six sections, in order:

| Section | What lives there |
|---|---|
| **Pilot** | Dashboard · Autopilot · AI Coach · Safety |
| **Models** | Installed Models · Download Model · Create Model |
| **Discover** | News (top-played Steam games + can-GamePilot-handle-this) |
| **Library** | Games · Logs · Settings (placeholder for v0.2) |

Each one is a different mode. Click around — nothing breaks.

## Dashboard

The home screen. Four big stat cards, four mode tiles, a recent-sessions list.

- **Stat cards** are placeholder numbers right now (Bosses beaten, AFK saves, Time saved, Multiplayer touched). They'll wire to your real stats in v0.2.
- **Mode tiles** — Beat Boss / Stay Alive / Build / Farm Resources. Click any one to read its blurb. They link into Autopilot setup.
- **Engage Autopilot** (the magenta-blue gradient button, top-right) — same as walking through Autopilot setup, but skipping the form. Use when you're confident.

## Autopilot

The setup page for "AI takes the controller for a bit."

What you see:

- A **vision mock** showing what the AI sees on your screen (silhouette + crosshair — placeholder until you hook a real screen feed).
- **Pre-flight checks** (6 of them). All green = you're allowed to engage. Multiplayer detected = blocked, period.
- **Mode** — pick one of the four (Beat Boss / Stay Alive / Build / Farm).
- **Time cap** — how long AI is allowed to play. Default 15 min. Hard ceiling 60.
- **Stop conditions** — when AI should hand control back even before the time cap (low HP, deaths, custom).
- **Emergency hotkey** — `Ctrl + Shift + Esc`. Memorise it.
- **Start Autopilot** — engages.

While engaged, all you have to know is: **Ctrl + Shift + Esc returns control instantly. Always.**

## AI Coach

Live chat with an AI that's looking at your screen.

You ask things in plain English:

- "i keep dying to the flurry attack, wtf do i do"
- "best dodge frames on this boss?"
- "take over for 1 try"

Coach answers grounded in what's actually on your screen. The right side shows what the AI sees (HP, scene, predicted next action).

Quick chips below the chat = canned questions. Click instead of typing.

## Safety

The most important screen. Read it.

- **Emergency Stop** card — the visual reminder of the hotkey. The big red icon pulses. That's intentional.
- **Guardrails** — toggles you can't turn off (single-player only, hard time cap, no memory injection) and ones you can (cap acknowledgement, pause on focus loss, anonymous telemetry — telemetry is **off** by default).
- **Session log** — every keypress AI made, with timestamps. Exportable.
- **This week** stats — emergency stops triggered, multiplayer blocks, cap reaches, average session.

If something feels wrong during a session, glance at this screen. The log is the source of truth.

## Models

Three sub-screens for managing the AI brains.

- **Installed Models** — what's on disk, which is active, source (local / Hugging Face / direct URL / created by you), status (active / idle).
- **Download Model** — pull a community model from Hugging Face, validate it, install it. ~30 seconds for ~300 MB.
- **Create Model** — train your own from gameplay you record. Eight-step wizard. Most gamers won't need this; advanced users only.

## News (Discover)

Top 10 most-played games on Steam right now, with **GamePilot's compatibility tier** stamped on each:

| Tier | Color | Meaning |
|---|---|---|
| **Supported** | green | One-click install. Pre-built model exists. |
| **Beta** | blue | Community model on Hugging Face. Validated but not battle-tested. |
| **Trainable** | amber | No model yet — but the genre is in scope. Train one via Create Model. |
| **Locked** | grey | We refuse. Anti-cheat (VAC, BattlEye) or competitive PvP. **Automation here gets you banned.** |

Locked rows show the reason in plain text underneath. We'd rather lose the rank position than lose your account.

The right rail shows trending games (biggest 24h player jumps) and a "Suggest a Game" button — opens a GitHub issue against the public compat index.

## Three commands you'll re-use forever

```
make start         # boot it up
make stop          # shut it down cleanly
make install       # update after `git pull`
```

That's the whole lifecycle.
