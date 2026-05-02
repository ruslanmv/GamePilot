# Safety, plain English

GamePilot is "AI plays for you." That sounds spicy. Here's exactly what we do — and don't do — to keep you out of trouble.

## The rules we enforce, no exceptions

### 1. Single-player only

Multiplayer and ranked are **blocked at the network layer.** Not "we recommend not." Not "be careful." Blocked. The autopilot loop refuses to engage if it detects an online lobby.

Why we're strict: anti-cheat systems (VAC, BattlEye, EAC) treat input automation as cheating. **They don't ask why.** One detected automation event in a competitive match = ban. We refuse to put your account in that path.

### 2. Anti-cheat-flagged games are locked

CS2, Dota 2, TF2, Apex (online), Valorant, etc. show up in the **News tab as "Locked"** with an explicit reason like:

> // #09 locked · vac anti-cheat blocks input injection · automation results in account ban

That's a load-bearing label. Don't try to "force it." There is no force-it.

### 3. Hard time cap

- Default session: **10 minutes.**
- Maximum allowed: **60 minutes.**
- AI returns control no matter what when the timer hits zero.

You can set lower. You can't go higher. There's an "Acknowledge cap ending" overlay that pops up 30s before — so you get the keyboard back gracefully, not mid-roll.

### 4. Emergency stop, always

**`Ctrl + Shift + Esc`**.

This hotkey is registered the moment GamePilot starts and only released when GamePilot exits. It:

1. Kills the autopilot loop instantly.
2. Returns keyboard + mouse to you.
3. Writes the abort to the session log.
4. Freezes the input layer for 2 seconds so no AI keypress leaks through during the handoff.

Memorise it. We put it on the Safety screen, on every Autopilot view, and in the dashboard pill — that's intentional.

### 5. No memory injection. No file modification.

GamePilot reads **pixels** from your screen and **presses keys** like a human. That's it.

It does **not**:

- Read game memory.
- Write to game files.
- Patch the game executable.
- Inject DLLs.
- Talk to anti-cheat hooks.

If you tear down a session and inspect what happened, you'll see screen captures and keystrokes. That's the whole surface.

## Things that are off by default

- **Anonymous telemetry.** Off. We'd love your help making the coach smarter, but only if you opt in. Toggle on Safety screen.
- **Cloud anything.** There is none. Models run on your machine.

## What we log (locally, never uploaded)

Every session writes a log to `~/.gamepilot/logs/` containing:

- Timestamps for engage / stop / cap-reached / emergency-stop.
- Every action AI took, with confidence score.
- Detected scene and HP / state values.
- Any blocked-action attempts (online lobby probe, multiplayer detected, etc).

Export from the Safety screen → you get a `.log` file you can read in Notepad. Useful when you're filing a bug.

## "What if I want to play multiplayer with a model that wasn't trained for it?"

You can't. We won't ship that ability.

If you want a tool to cheat in online games, GamePilot is the wrong tool. There are scummier projects for that. We'll keep being the boring, safe one.

## "What if my account *does* get flagged?"

Tell us immediately. Open a GitHub issue with:

- Game + appid.
- The session log (Safety → Export).
- Game version + anti-cheat in use (if known).

If GamePilot triggered a flag, that's a P0 bug for us. We'll patch the compat index to mark that game Locked, and look at what we missed.

## The promise

> Your game. Your time. Your choice.

We mean it. The product is built to keep gaming fun — not to ship cheats. Every safety guardrail is the default because that's how it should be, not as an afterthought you have to opt in to.

If anything in GamePilot ever feels like it's working *against* that promise, that's a bug. File it.
