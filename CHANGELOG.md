# Changelog

All notable changes to GamePilot are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with [PEP 440](https://peps.python.org/pep-0440/) pre-release identifiers.

## [Unreleased]

## [0.1.0b1] - 2026-05-01

### 🚀 First Public Beta on PyPI

This is the initial public release of GamePilot, published as a beta
pre-release for early adopters and testers.

### Added

#### Universal Core Models
- `gamepilot.core.observation` – universal observation model
- `gamepilot.core.action` – universal action model
- `gamepilot.core.world_state` – universal world state
- `gamepilot.core.events` – event and goal systems
- `gamepilot.core.memory` – experience and session memory

#### Environment Abstractions
- `gamepilot.environments.base` – base environment interface
- `gamepilot.environments.screen_observer` – real-time screen capture
- `gamepilot.environments.video_observer` – video file analysis
- `gamepilot.environments.companion_only` – chat-only mode (safest)
- `gamepilot.environments.private_sandbox` – safe automated testing

#### Safety Systems
- `gamepilot.safety.guardrails` – safety checks and rules
- `gamepilot.safety.permissions` – permission management
- `gamepilot.safety.rate_limit` – action rate limiting

#### AI Companion
- Multi-provider LLM support (OpenAI, watsonx, Anthropic, Mock)
- Natural language understanding and intent parsing
- Contextual game state awareness
- Conversation history tracking

#### Construction Domain
- Step-by-step building plans
- Resource optimization
- 6 structure templates
- Material flexibility

#### Domain Profiles
- `profiles/domains/survival_sandbox.yaml` – Minecraft, Terraria, Valheim, etc.
- `profiles/domains/open_world_rpg.yaml` – Skyrim, Elden Ring, Zelda, etc.
- `profiles/domains/construction_sandbox.yaml` – creative building games

#### Packaging
- Wheel and sdist build via `setuptools` with automatic subpackage discovery
  (`[tool.setuptools.packages.find]`).
- Console entry point: `gamepilot` → `gamepilot.app.main:main`.
- Optional extras: `companion`, `vision`, `screen`, `control`, `ml`,
  `training`, `voice`, `all`, plus dev tooling under `dev`.

### Installation

```bash
# Minimal (API + core only)
pip install --pre gamepilot

# With AI companion
pip install --pre "gamepilot[companion]"

# With computer vision
pip install --pre "gamepilot[vision]"

# Everything
pip install --pre "gamepilot[all]"
```

The `--pre` flag is required because `0.1.0b1` is a beta pre-release.

### Known Limitations (Beta)

- Some optional integrations (`torch`, `cv2`, `ultralytics`, etc.) are gated
  behind extras and only validated when those extras are installed.
- The `tests/` suite skips torch / OpenCV-dependent tests when those
  optional dependencies are absent.
- API is **not** considered stable until `1.0.0`.

## [0.0.0] - 2026-04-01

### Added

- Initial project scaffolding: repository layout, license, contributing
  guidelines, and internal prototypes that fed into `0.1.0b1`.
- Pre-PyPI development on GitHub only; no published artifacts.

---

## Roadmap

- **v0.1.0** – Promote the beta to a stable patch release once the API
  surface and packaging are validated by early adopters.
- **v0.2.0** – Voice interaction, additional domain profiles.
- **v0.3.0** – Learning from demonstrations.
- **v1.0.0** – Stable plugin platform with frozen public API.

[Unreleased]: https://github.com/ruslanmv/gamepilot/compare/v0.1.0b1...HEAD
[0.1.0b1]: https://github.com/ruslanmv/gamepilot/releases/tag/v0.1.0b1
[0.0.0]: https://github.com/ruslanmv/gamepilot/releases/tag/v0.0.0
