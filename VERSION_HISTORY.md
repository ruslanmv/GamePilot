# GamePilot Version History

This document records the public version timeline of GamePilot. For a
detailed per-release breakdown of changes, see [`CHANGELOG.md`](CHANGELOG.md).

## Released

### v0.1.0b1 — 2026-05-01 (current)

- **Status:** Beta pre-release on PyPI.
- **Scope:** First public release. Universal core models, environment
  abstractions, safety systems, AI companion, construction domain,
  domain profiles, and full PyPI packaging with optional extras.
- **Install:** `pip install --pre gamepilot`

### v0.0.0 — 2026-04-01

- **Status:** Pre-PyPI development snapshot.
- **Scope:** Initial scaffolding, internal prototyping, and architecture
  iteration. Not published to PyPI.

## Planned

| Version    | Theme                                    | Status   |
|------------|------------------------------------------|----------|
| v0.1.0     | Stable patch promoted from `0.1.0b1`     | Planned  |
| v0.2.0     | Voice interaction, more domain profiles  | Planned  |
| v0.3.0     | Learning from demonstrations             | Planned  |
| v1.0.0     | Frozen public API, plugin platform       | Future   |

## Versioning Policy

- Public versions follow [Semantic Versioning](https://semver.org).
- Pre-release tags follow [PEP 440](https://peps.python.org/pep-0440/)
  (`aN`, `bN`, `rcN`).
- The `0.x.y` line is **not** API-stable — breaking changes can land
  in any minor bump until `1.0.0`.

## Authors

- **Ruslan Magana Vsevolodovna** — `<contact@ruslanmv.com>`

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to get involved.
