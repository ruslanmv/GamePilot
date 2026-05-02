"""Thin wrapper around Valve's public Steam endpoints.

Two endpoints are used, neither of which requires an API key:

* ``ISteamChartsService/GetMostPlayedGames/v1/`` — concurrent-player ranks.
* ``store.steampowered.com/api/appdetails`` — per-app metadata.

The functions here are intentionally small and pure-ish so they can be
mocked or swapped in tests without touching the network.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import requests

MOST_PLAYED_URL = "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/"
APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"

DEFAULT_TIMEOUT = 20
DEFAULT_USER_AGENT = "GamePilot/0.1 (+https://github.com/ruslanmv/GamePilot)"


@dataclass
class SteamClient:
    """Minimal Steam client. Override ``session`` in tests to inject a stub."""

    session: requests.Session = field(default_factory=requests.Session)
    timeout: int = DEFAULT_TIMEOUT
    user_agent: str = DEFAULT_USER_AGENT

    def __post_init__(self) -> None:
        self.session.headers.setdefault("User-Agent", self.user_agent)
        self.session.headers.setdefault("Accept", "application/json")

    def _get_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_top_played_games(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return the top ``limit`` games by current concurrent players."""
        data = self._get_json(MOST_PLAYED_URL)
        ranks = data.get("response", {}).get("ranks", [])
        return ranks[: max(0, int(limit))]

    def get_app_details(self, appid: int) -> Dict[str, Any]:
        """Return public store metadata for a single app, or ``{}`` on miss."""
        data = self._get_json(
            APP_DETAILS_URL,
            params={
                "appids": appid,
                # Restrict the payload — the full appdetails response is huge.
                "filters": (
                    "basic,genres,price_overview,platforms,"
                    "metacritic,recommendations,release_date,categories"
                ),
            },
        )
        app_data = data.get(str(appid), {}) if isinstance(data, dict) else {}
        if not app_data.get("success"):
            return {}
        return app_data.get("data", {}) or {}


# Module-level helpers preserve the API shape the user pasted in their brief
# so they can be called directly without instantiating SteamClient.

_default_client = SteamClient()


def get_top_played_games(limit: int = 10) -> List[Dict[str, Any]]:
    return _default_client.get_top_played_games(limit=limit)


def get_app_details(appid: int) -> Dict[str, Any]:
    return _default_client.get_app_details(appid)


def simplify_game_info(rank_item: Dict[str, Any], position: int) -> Dict[str, Any]:
    """Combine a chart rank entry with its store metadata into a flat dict."""
    appid = int(rank_item["appid"])
    details = get_app_details(appid)

    return {
        "rank": position,
        "appid": appid,
        "name": details.get("name") or rank_item.get("name"),
        "current_players": rank_item.get("concurrent_in_game"),
        "peak_players_today": rank_item.get("peak_in_game"),
        "store_url": f"https://store.steampowered.com/app/{appid}",
        "steamdb_url": f"https://steamdb.info/app/{appid}",
        "header_image": details.get("header_image"),
        "release_date": (details.get("release_date") or {}).get("date"),
        "developers": details.get("developers") or [],
        "publishers": details.get("publishers") or [],
        "price": (details.get("price_overview") or {}).get("final_formatted")
        or ("Free to Play" if details.get("is_free") else None),
        "genres": [g["description"] for g in details.get("genres") or []],
        "platforms": details.get("platforms") or {},
        "recommendations": (details.get("recommendations") or {}).get("total"),
        "metacritic_score": (details.get("metacritic") or {}).get("score"),
    }
