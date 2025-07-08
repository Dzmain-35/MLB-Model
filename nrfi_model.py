import sqlite3
import pandas as pd
from datetime import datetime

def safe_parse_ip(ip_str):
    """Convert innings_pitched like '6.1' to float."""
    try:
        if "." in ip_str:
            whole, frac = ip_str.split(".")
            return int(whole) + int(frac) * (1/3)
        return float(ip_str)
    except:
        return 0.0

def build_pitcher_stats(df_pitchers):
    df_pitchers["ip"] = df_pitchers["innings_pitched"].apply(safe_parse_ip)
    df_pitchers["date"] = pd.to_datetime(df_pitchers["date"])
    return df_pitchers

def load_nrfi_games_with_pitchers(db_path="mlb_stats.db"):
    conn = sqlite3.connect(db_path)

    games = pd.read_sql_query("""
        SELECT id AS game_id, date, home_team, away_team,
               home_pitcher, away_pitcher,
               home_1st_runs, away_1st_runs,
               CASE WHEN home_1st_runs + away_1st_runs > 0 THEN 1 ELSE 0 END AS yrfi
        FROM games
        WHERE home_pitcher IS NOT NULL AND away_pitcher IS NOT NULL
              AND home_1st_runs IS NOT NULL AND away_1st_runs IS NOT NULL
        ORDER BY date
    """, conn)

    pitchers = pd.read_sql_query("""
        SELECT p.*, g.date
        FROM pitchers p
        JOIN games g ON g.id = p.game_id
    """, conn)

    conn.close()

    pitchers = build_pitcher_stats(pitchers)
    games["date"] = pd.to_datetime(games["date"])
    team_trends = games.copy()

    features = []
    for _, row in games.iterrows():
        game_date = row["date"]
        home_team = row["home_team"]
        away_team = row["away_team"]
        home_pitcher = row["home_pitcher"]
        away_pitcher = row["away_pitcher"]

        # Team-level YRFI rate (last 20 games)
        home_team_games = team_trends[(team_trends["home_team"] == home_team) & (team_trends["date"] < game_date)].tail(20)
        away_team_games = team_trends[(team_trends["away_team"] == away_team) & (team_trends["date"] < game_date)].tail(20)

        home_team_yrfi_rate = (home_team_games["home_1st_runs"] > 0).mean() if not home_team_games.empty else None
        away_team_yrfi_rate = (away_team_games["away_1st_runs"] > 0).mean() if not away_team_games.empty else None

        def pitcher_yrfi_rate(df, name, before_date):
            games = df[(df["name"] == name) & (df["date"] < before_date)]
            if games.empty:
                return None
            return (games["earned_runs"] > 0).mean()

        home_pitcher_yrfi = pitcher_yrfi_rate(pitchers, home_pitcher, game_date)
        away_pitcher_yrfi = pitcher_yrfi_rate(pitchers, away_pitcher, game_date)

        home_p = pitchers[(pitchers["name"] == home_pitcher) & (pitchers["date"] < game_date)]
        away_p = pitchers[(pitchers["name"] == away_pitcher) & (pitchers["date"] < game_date)]

        def pitcher_metrics(df):
            ip = df["ip"].sum()
            if ip == 0: return (None, None)
            era = df["earned_runs"].sum() / ip * 9
            k9 = df["strikeouts"].sum() / ip * 9
            return (era, k9)

        home_era, home_k9 = pitcher_metrics(home_p)
        away_era, away_k9 = pitcher_metrics(away_p)

        features.append({
            "game_id": row["game_id"],
            "date": game_date,
            "home_team": home_team,
            "away_team": away_team,
            "home_pitcher": home_pitcher,
            "away_pitcher": away_pitcher,
            "home_pitcher_era": home_era,
            "home_pitcher_k9": home_k9,
            "away_pitcher_era": away_era,
            "away_pitcher_k9": away_k9,
            "home_pitcher_yrfi_rate": home_pitcher_yrfi,
            "away_pitcher_yrfi_rate": away_pitcher_yrfi,
            "home_team_yrfi_rate": home_team_yrfi_rate,
            "away_team_yrfi_rate": away_team_yrfi_rate,
            "yrfi": row["yrfi"]
        })

    df_feat = pd.DataFrame(features)
    df_feat.to_csv("nrfi_features_enhanced.csv", index=False)
    df_feat.dropna(inplace=True)
    return df_feat

if __name__ == "__main__":
    df = load_nrfi_games_with_pitchers()
    print(df.head())
    print(df.columns.tolist())
