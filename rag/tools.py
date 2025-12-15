import requests
from agno.tools import tool

API = "https://www.speedrun.com/api/v1"

SA2_GAME = {"id": "l3dx0vdy", "name": "Sonic Adventure 2: Battle"}
SA2_EXTENSIONS = {"id": "k6q3291g", "name": "Sonic Adventure 2: Battle - Category Extensions"}

def _http_get(url, params=None):
    try:
        r = requests.get(url, params=params or {}, timeout=15)
        r.raise_for_status()
        return {"ok": True, "json": r.json()}
    except requests.HTTPError as e:
        return {
            "ok": False,
            "error": f"HTTPError: {e}",
            "status_code": getattr(e.response, "status_code", None),
            "body": getattr(e.response, "text", None),
            "url": url,
            "params": params or {},
        }
    except requests.RequestException as e:
        return {"ok": False, "error": f"RequestException: {e}", "url": url, "params": params or {}}

@tool
def get_sa2_categories(use_extensions: bool = False):
    """Returns category dictionary for SA2 or CatExt."""
    game = SA2_EXTENSIONS if use_extensions else SA2_GAME
    resp = _http_get(f"{API}/games/{game['id']}/categories")
    if not resp["ok"]:
        return {"error": "Failed to fetch categories", "debug": resp}
    return {"game": game, "categories": resp["json"]}

@tool
def get_sa2_leaderboard(category_id: str, use_extensions: bool = False, top: int = 1):
    """Gets leaderboard by category_id."""
    game = SA2_EXTENSIONS if use_extensions else SA2_GAME
    url = f"{API}/leaderboards/{game['id']}/category/{category_id}"
    params = {"top": max(1, int(top))}
    resp = _http_get(url, params=params)
    if not resp["ok"]:
        return {"error": "Leaderboard request failed", "debug": resp}
    return {"game": game, "category_id": category_id, "leaderboard": resp["json"]}
