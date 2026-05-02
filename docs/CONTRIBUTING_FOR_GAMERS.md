# Contributing (you don't have to be a dev)

You don't need to write code to make GamePilot better. The most useful contributions from gamers are the ones devs can't do alone.

## The four ways to help, in order of "easiest first"

### 1. Suggest a game for the compatibility index

You play a game. It's not in the News tab top 10, or it's listed but the tier is wrong. Tell us.

**How:**

- Open [github.com/ruslanmv/GamePilot/issues/new](https://github.com/ruslanmv/GamePilot/issues/new)
- Title: `Suggest: <Game Name> (appid <number>)`
- Include the Steam appid (the number in the Steam URL — e.g. Elden Ring is `1245620`).
- Tell us: which mode would you want? (Beat Boss / Stay Alive / Build / Farm)
- If you know whether the game has anti-cheat, mention it.

Click "Suggest a Game" in the News tab → it pre-fills this for you.

### 2. Report a bug

You hit something weird. **Read [IF_SOMETHING_BREAKS.md](IF_SOMETHING_BREAKS.md)** first to make sure it's not already handled, then file an issue with:

1. What you tried.
2. What happened (error message verbatim).
3. Your OS.
4. The last 40 lines of `logs/gamepilot-server.log`.

That's it. We don't need a stack trace or a repro script. Plain language is fine.

### 3. Improve the docs

You hit something confusing in these docs. Or a fix for an error wasn't here and we made you suffer.

**How:**

- Find the doc on [github.com/ruslanmv/GamePilot/tree/main/docs](https://github.com/ruslanmv/GamePilot/tree/main/docs)
- Click the pencil ✏️ icon top-right → "Fork this repository and propose changes"
- Edit, write what you wish had been there, hit "Propose changes."

GitHub walks you through it. No git knowledge required for tiny edits.

### 4. Test pre-release builds

When we cut a beta, we sometimes ask for testers in the Discord / GitHub Discussions. If you have time and a curiosity for breaking things, that's gold to us.

We need:

- Different OSes (Windows 10/11, macOS Intel + Apple Silicon, various Linux distros).
- Different games (especially ones not in our daily rotation).
- Different network setups (corporate firewall, IPv6-only, etc).

You install the beta, you do your normal session, you tell us what felt off. That's the contribution.

---

## If you DO want to write code

Cool. You don't have to be a Python expert.

### The dev setup is the same as the gamer setup

```
git clone https://github.com/ruslanmv/GamePilot.git
cd GamePilot
make install-dev   # extra: pulls pytest, black, etc.
```

### Run tests before you push

```
make test
```

Three batches will probably pass; if your change breaks one, the test name tells you which behaviour you broke. Fix, re-run, push.

### Format your code

```
make format       # runs black + ruff
make lint         # runs flake8 + pylint
```

Don't argue with the formatter. Let it win. It saves arguments later.

### What's a "small fix"?

If you want to test the waters, here's a list of things that don't need deep familiarity:

- A typo in a doc.
- A new entry in `gamepilot/app/discover/compatibility_index.json` (the compat index — adding a game with a known tier).
- A new question in the AI Coach quick-chips list (`frontend/app.html`, search for `class="quick"`).
- A new error case in `IF_SOMETHING_BREAKS.md`.
- A test case in `tests/` that exercises something currently uncovered.

Bigger refactors? Open an issue first to discuss. Saves both of us time.

### The branch + PR flow

```
git checkout -b your-fix-name
# edit, edit
git add <files>
git commit -m "Short message about what you did"
git push -u origin your-fix-name
```

Then open a PR on GitHub. We'll review within a few days. **Be patient — we're a small team.**

### Commit message style

- First line: imperative, ≤ 70 chars. ("Add X", "Fix Y", "Update Z")
- Blank line.
- Body: why you did it. Not what (the diff shows that).

Example:

```
Mark Helldivers 2 as Locked in compat index

Game uses nProtect GameGuard at the kernel level. Input automation
trips it within the first 30s. Locked tier with explicit reason so
the News tab shows "automation results in account ban."
```

That's a great commit message. Three lines, all useful.

---

## What we will and won't merge

**We will merge:**

- Fixes for actual bugs.
- New compat-index entries with evidence (your session log, or a community thread linking automation to bans).
- Doc clarifications.
- New tests.
- New game profiles for **single-player** scenarios.

**We won't merge:**

- Features that defeat anti-cheat or read game memory.
- Tools to evade kernel-level anti-cheats.
- Any code path that would touch a multiplayer / ranked session.
- Telemetry that uploads gameplay without explicit opt-in.

If your PR falls in the "won't merge" bucket and you think we're wrong, open an issue first to discuss. We're not going to argue in PR comments.

---

## Thanks

Seriously. The reason this project keeps getting better is the people who:

- Filed an issue with a clean error log instead of "it broke."
- Added a one-line entry to the compat index.
- Caught a typo in a doc.
- Tested a beta on a weird Windows setup.

You're the brand. Thanks for showing up.
