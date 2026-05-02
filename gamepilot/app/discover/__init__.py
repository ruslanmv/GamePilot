"""GamePilot Discover — Steam most-played + GamePilot compatibility.

Two pieces:

* :mod:`steam_client` — small wrapper around Valve's public charts and
  store-details endpoints (no key required).
* :mod:`compatibility` — overlays GamePilot's local compatibility index
  on top of the Steam ranks, returning a tier per game.

The :class:`NewsService` here glues them together with a 5-minute cache so
the FastAPI ``/news`` route can answer cheaply on every page load.
"""

from .compatibility import (
    COMPAT_BETA,
    COMPAT_LOCKED,
    COMPAT_SUPPORTED,
    COMPAT_TRAINABLE,
    CompatibilityIndex,
    classify,
)
from .news_service import NewsService, build_news_service
from .steam_client import (
    SteamClient,
    get_app_details,
    get_top_played_games,
    simplify_game_info,
)

__all__ = [
    "COMPAT_BETA",
    "COMPAT_LOCKED",
    "COMPAT_SUPPORTED",
    "COMPAT_TRAINABLE",
    "CompatibilityIndex",
    "NewsService",
    "SteamClient",
    "build_news_service",
    "classify",
    "get_app_details",
    "get_top_played_games",
    "simplify_game_info",
]
