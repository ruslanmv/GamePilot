"""GamePilot compatibility classifier for Steam apps.

The ``compatibility_index.json`` ships with the app and is updated
server-side. It maps Steam ``appid`` to one of four tiers:

* ``supported`` — pre-built model profile, one-click install.
* ``beta`` — community model on Hugging Face, validated.
* ``trainable`` — no model yet but the genre/engine is in scope.
* ``locked`` — anti-cheat blocks input automation, or genre is out of
  scope (typically competitive PvP). Always shown with an explicit
  reason — never silently hidden.

Unknown apps fall through to a ``trainable``/``locked`` decision based
on genre rules so the News tab stays useful even before the index ships
support for a freshly trending title.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

COMPAT_SUPPORTED = "supported"
COMPAT_BETA = "beta"
COMPAT_TRAINABLE = "trainable"
COMPAT_LOCKED = "locked"

VALID_TIERS = {COMPAT_SUPPORTED, COMPAT_BETA, COMPAT_TRAINABLE, COMPAT_LOCKED}

# Genres / categories that are always locked because automation would be
# bannable or technically blocked. Match is case-insensitive substring.
LOCK_GENRE_KEYWORDS: Tuple[str, ...] = (
    "massively multiplayer",
    "moba",
    "esports",
    "competitive",
)

# Anti-cheat / category strings that imply input injection is blocked.
LOCK_CATEGORY_KEYWORDS: Tuple[str, ...] = (
    "vac",
    "anti-cheat",
    "battleye",
    "easy anti-cheat",
)

DEFAULT_INDEX_PATH = Path(__file__).resolve().parent / "compatibility_index.json"


@dataclass
class CompatEntry:
    tier: str
    profile: Optional[str] = None
    reason: Optional[str] = None
    note: Optional[str] = None


@dataclass
class CompatibilityIndex:
    """In-memory view of the compatibility index file."""

    entries: Dict[int, CompatEntry]
    version: str = "0.0.0"
    updated_at: Optional[str] = None
    source_path: Optional[Path] = None

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "CompatibilityIndex":
        path = path or DEFAULT_INDEX_PATH
        if not path.exists():
            return cls(entries={}, source_path=path)
        with path.open("r", encoding="utf-8") as fh:
            blob = json.load(fh)
        raw_entries = blob.get("entries", {}) or {}
        entries: Dict[int, CompatEntry] = {}
        for appid_str, payload in raw_entries.items():
            try:
                appid = int(appid_str)
            except (TypeError, ValueError):
                continue
            tier = (payload or {}).get("tier", COMPAT_TRAINABLE)
            if tier not in VALID_TIERS:
                tier = COMPAT_TRAINABLE
            entries[appid] = CompatEntry(
                tier=tier,
                profile=(payload or {}).get("profile"),
                reason=(payload or {}).get("reason"),
                note=(payload or {}).get("note"),
            )
        return cls(
            entries=entries,
            version=blob.get("version", "0.0.0"),
            updated_at=blob.get("updated_at"),
            source_path=path,
        )

    def lookup(self, appid: int) -> Optional[CompatEntry]:
        return self.entries.get(int(appid))

    def counts(self) -> Dict[str, int]:
        out = {tier: 0 for tier in VALID_TIERS}
        for entry in self.entries.values():
            out[entry.tier] = out.get(entry.tier, 0) + 1
        return out


def _matches_any(haystack: Iterable[str], needles: Iterable[str]) -> bool:
    bag = " ".join(s.lower() for s in haystack if isinstance(s, str))
    return any(needle in bag for needle in needles)


def _genre_strings(game: Dict[str, Any]) -> List[str]:
    return [g for g in (game.get("genres") or []) if isinstance(g, str)]


def _category_strings(game: Dict[str, Any]) -> List[str]:
    cats = game.get("categories") or []
    out: List[str] = []
    for cat in cats:
        if isinstance(cat, str):
            out.append(cat)
        elif isinstance(cat, dict) and "description" in cat:
            out.append(cat["description"])
    return out


def classify(
    game: Dict[str, Any],
    index: Optional[CompatibilityIndex] = None,
) -> CompatEntry:
    """Decide a tier for one simplified game dict.

    Resolution order:

    1. Explicit entry in the compatibility index (always wins).
    2. Genre / category locks (PvP, anti-cheat) → ``locked`` with reason.
    3. Default → ``trainable`` (every other game can be trained for via
       the Create Model wizard).
    """
    appid = int(game.get("appid") or 0)
    idx = index or CompatibilityIndex.load()

    explicit = idx.lookup(appid) if appid else None
    if explicit is not None:
        return explicit

    genres = _genre_strings(game)
    categories = _category_strings(game)

    if _matches_any(categories, LOCK_CATEGORY_KEYWORDS):
        return CompatEntry(
            tier=COMPAT_LOCKED,
            reason="anti-cheat blocks input injection · automation results in account ban",
        )
    if _matches_any(genres, LOCK_GENRE_KEYWORDS):
        return CompatEntry(
            tier=COMPAT_LOCKED,
            reason="competitive / online-only genre · automation is bannable",
        )

    return CompatEntry(
        tier=COMPAT_TRAINABLE,
        note="no profile yet · open the Create Model wizard to train one",
    )
