## Thin client for the FBR API (https://fbrapi.com).

from __future__ import annotations

import pandas as pd
import time
from typing import Any, Dict, Optional, List


import requests

# ---------- Configuration knobs (tune if you hit issues) ----------

BASE = "https://fbrapi.com"

# How long to sleep after *any* successful request. Adjust if you see rate-limit responses.
RATE_LIMIT_SLEEP_SECONDS = 3.0

REQUEST_TIMEOUT = 30  # seconds


# Use a single Session for connection reuse (faster + fewer TCP handshakes).
SESSION = requests.Session()

# Generated key + when we generated it (for optional soft TTL).
GEN_KEY: Optional[str] = None

def generate_api_key() -> str:
    print("Generating new FBR API key...")
    resp = SESSION.post(f"{BASE}/generate_api_key", timeout=30)
    resp.raise_for_status()
    data = resp.json()
    key = data.get("api_key")
    if not key:
        raise RuntimeError("FBR /generate_api_key did not return 'api_key'.")
    return key

def print_API_Key(key: str) -> None:
    print("=== FBR API Key Generated ===")
    print("To avoid rate-limiting, please set the following environment variable:")
    print()
    print(f"  export FBR_API_KEY={key}")
    print()
    print("You can also add this line to your shell profile (e.g. ~/.bashrc).")
    print("This key is valid for 24 hours.")
    print("=============================")

def get_leagues(country: str) -> Dict[str, Any]:
    print("Fetching leagues from FBR API...")
    global GEN_KEY
    MAX_TRIES = 3
    ATTEMPT = 0
    if GEN_KEY is None:
            print("No API key found, generating a new one.")
            GEN_KEY = generate_api_key()
    print("Using API key:", GEN_KEY)
    headers = {"X-API-Key": f"{GEN_KEY}"}
    resp = SESSION.get(f"{BASE}/leagues", headers=headers, params={"country_code": country, "gender": "M"})
    if resp.status_code in (401, 403) and ATTEMPT < MAX_TRIES:
        print(f"API key rejected (status {resp.status_code}). Generating a new key and retrying...")
        GEN_KEY = generate_api_key()
        ATTEMPT += 1
        get_leagues(country)
    resp.raise_for_status()
    time.sleep(RATE_LIMIT_SLEEP_SECONDS)
    print(resp.json())
    return resp.json()

def get_seasons(league_id: int) -> Dict[str, Any]:
    print(f"Fetching seasons for league_id={league_id} from FBR API...")
    global GEN_KEY
    MAX_TRIES = 3
    ATTEMPT = 0
    if GEN_KEY is None:
        print("No API key found, generating a new one.")
        GEN_KEY = generate_api_key()
    print("Using API key:", GEN_KEY)
    headers = {"X-API-Key": f"{GEN_KEY}"}
    resp = SESSION.get(f"{BASE}/league-seasons", headers=headers, params={"league_id": league_id})
    if resp.status_code in (401, 403) and ATTEMPT < MAX_TRIES:
        print(f"API key rejected (status {resp.status_code}). Generating a new key and retrying...")
        GEN_KEY = generate_api_key()
        ATTEMPT += 1
        get_seasons(league_id)
    resp.raise_for_status()
    time.sleep(RATE_LIMIT_SLEEP_SECONDS)
    return resp.json()

def flatten_leagues_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Turn the nested structure into a simple list of league dicts, each with league_type.
    """
    rows: List[Dict[str, Any]] = []
    for bucket in (payload or {}).get("data", []):
        league_type = bucket.get("league_type")
        for lg in bucket.get("leagues", []):
            # lg already contains fields like league_id, competition_name, gender, etc.
            if lg.get("gender") == "M":
                rows.append({"league_type": league_type, **lg})   
    return rows

def flatten_seasons_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    
    rows: List[Dict[str, Any]] = []
    for bucket in (payload or {}).get("data", []):
        season_id = bucket.get("league_id")
        for season in bucket.get("season_id", []):
            rows.append(season)   
    return rows

def leagues_to_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows)

def main() -> None:
    print("FBR API Thin Client")
    payload = get_leagues("ENG")      
    league_rows = flatten_leagues_payload(payload)     # dict with nested 'data'
    df = leagues_to_df(league_rows)            # flat table
    print(df.head(10))                     # quick peek

    # Example: find Premier League id
    epl_row = df[(df["competition_name"] == "Premier League") & (df["gender"] == "M")].head(1)
    if not epl_row.empty:
        epl_id = int(epl_row.iloc[0]["league_id"])
        print("Premier League league_id =", epl_id)  # often 9
        seasons_payload = get_seasons(epl_id)
        print("Seasons payload:", seasons_payload)
        seasons_rows = flatten_seasons_payload(seasons_payload)

if __name__ == "__main__":
    main()