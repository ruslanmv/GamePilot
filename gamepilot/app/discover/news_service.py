"""News service: top-played Steam games tagged with GamePilot compatibility.

Single entrypoint :class:`NewsService.fetch` returns a payload shaped
exactly the way the News tab in ``frontend/app.html`` expects, so the
FastAPI route can simply hand it back as JSON.

A 5-minute cache is held in process: the SteamCharts API is happy to be
hit once per page load, but we don't need to do it on every navigation.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, List, Optional

from .compatibility import CompatibilityIndex, classify
from .steam_client import SteamClient

LOG = logging.getLogger(__name__)

DEFAULT_CACHE_TTL = 5 * 60  # 5 minutes
DEFAULT_LIMIT = 10


def _genre_summary(simplified: Dict[str, Any]) -> str:
    genres = simplified.get("genres") or []
    if not genres:
        return "—"
    return genres[0]


def _meta_line(simplified: Dict[str, Any]) -> str:
    parts: List[str] = []
    rd = simplified.get("release_date")
    if rd:
        parts.append(str(rd).split(",")[-1].strip()[-4:] or rd)
    devs = simplified.get("developers") or []
    if devs:
        parts.append(devs[0])
    return " · ".join(parts) if parts else "—"


@dataclass
class NewsService:
    """Fetches Steam ranks + classifies them, with a small in-memory cache."""

    client: SteamClient = field(default_factory=SteamClient)
    index: CompatibilityIndex = field(default_factory=CompatibilityIndex.load)
    cache_ttl: int = DEFAULT_CACHE_TTL

    _cache: Optional[Dict[str, Any]] = field(default=None, init=False, repr=False)
    _cached_at: float = field(default=0.0, init=False, repr=False)
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def fetch(self, limit: int = DEFAULT_LIMIT, force: bool = False) -> Dict[str, Any]:
        """Return the news payload, refreshing from Steam at most every TTL."""
        now = time.time()
        with self._lock:
            fresh = (
                self._cache is not None
                and (now - self._cached_at) < self.cache_ttl
                and len(self._cache.get("games", [])) >= min(limit, DEFAULT_LIMIT)
            )
            if fresh and not force:
                return _slice(self._cache, limit)

            try:
                payload = self._build(limit=limit)
                self._cache = payload
                self._cached_at = now
                return _slice(payload, limit)
            except Exception as exc:  # noqa: BLE001
                LOG.warning("News fetch failed: %s", exc)
                if self._cache is not None:
                    stale = dict(self._cache)
                    stale["status"] = "stale"
                    stale["error"] = str(exc)
                    stale["age_seconds"] = int(now - self._cached_at)
                    return _slice(stale, limit)
                return {
                    "status": "error",
                    "error": str(exc),
                    "fetched_at": int(now),
                    "compat_index_version": self.index.version,
                    "filters": [],
                    "games": [],
                }

    def _build(self, limit: int) -> Dict[str, Any]:
        ranks = self.client.get_top_played_games(limit=limit)
        games: List[Dict[str, Any]] = []
        for position, rank_item in enumerate(ranks, start=1):
            try:
                appid = int(rank_item.get("appid"))
            except (TypeError, ValueError):
                continue
            details = self.client.get_app_details(appid)
            simplified = _simplify(rank_item, position, details)
            tier_entry = classify(simplified, index=self.index)
            simplified["compatibility"] = {
                "tier": tier_entry.tier,
                "profile": tier_entry.profile,
                "reason": tier_entry.reason,
                "note": tier_entry.note,
            }
            simplified["meta_line"] = _meta_line(simplified)
            simplified["primary_genre"] = _genre_summary(simplified)
            games.append(simplified)

        filters = _filter_counts(games)
        fetched = int(time.time())
        return {
            "status": "ok",
            "fetched_at": fetched,
            "compat_index_version": self.index.version,
            "compat_index_updated_at": self.index.updated_at,
            "filters": filters,
            "games": games,
        }


def _simplify(rank_item: Dict[str, Any], position: int, details: Dict[str, Any]) -> Dict[str, Any]:
    appid = int(rank_item["appid"])
    return {
        "rank": position,
        "appid": appid,
        "name": (details.get("name") if details else None) or rank_item.get("name") or f"App {appid}",
        "current_players": rank_item.get("concurrent_in_game"),
        "peak_players_today": rank_item.get("peak_in_game"),
        "store_url": f"https://store.steampowered.com/app/{appid}",
        "steamdb_url": f"https://steamdb.info/app/{appid}",
        "header_image": details.get("header_image") if details else None,
        "release_date": (details.get("release_date") or {}).get("date") if details else None,
        "developers": details.get("developers") or [] if details else [],
        "publishers": details.get("publishers") or [] if details else [],
        "price": (
            (details.get("price_overview") or {}).get("final_formatted")
            or ("Free to Play" if details.get("is_free") else None)
        )
        if details
        else None,
        "genres": [g["description"] for g in (details.get("genres") or [])] if details else [],
        "platforms": details.get("platforms") or {} if details else {},
        "recommendations": (details.get("recommendations") or {}).get("total") if details else None,
        "metacritic_score": (details.get("metacritic") or {}).get("score") if details else None,
    }


def _filter_counts(games: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counts = {"all": len(games), "supported": 0, "beta": 0, "trainable": 0, "locked": 0}
    for g in games:
        tier = (g.get("compatibility") or {}).get("tier")
        if tier in counts:
            counts[tier] += 1
    return [{"key": key, "label": key.title(), "count": counts[key]} for key in ("all", "supported", "beta", "trainable", "locked")]


def _slice(payload: Dict[str, Any], limit: int) -> Dict[str, Any]:
    if limit >= len(payload.get("games", [])):
        return payload
    sliced = dict(payload)
    sliced["games"] = payload["games"][:limit]
    sliced["filters"] = _filter_counts(sliced["games"])
    return sliced


_default_service: Optional[NewsService] = None
_default_service_lock = Lock()


def build_news_service() -> NewsService:
    """Return a process-wide singleton service. Safe to import lazily."""
    global _default_service
    with _default_service_lock:
        if _default_service is None:
            _default_service = NewsService()
        return _default_service
