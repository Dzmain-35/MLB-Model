import statsapi
import sqlite3
import pandas as pd
import joblib
from datetime import datetime
from nrfi_model import build_pitcher_stats, safe_parse_ip

# Load trained model
model = joblib.load("nrfi_model.pkl")

def get_historical_data():
    conn = sqlite3.connect("mlb_stats.db")

    pitchers = pd.read_sql_query("""
        SELECT p.*, g.date
        FROM pitchers p
        JOIN games g ON g.id = p.game_id
    """, conn)

    games = pd.read_sql_query("""
        SELECT * FROM games
        WHERE home_1st_runs IS NOT NULL AND away_1st_runs IS NOT NULL
    """, conn)

    conn.close()

    pitchers = build_pitcher_stats(pitchers)
    games["date"] = pd.to_datetime(games["date"])
    return pitchers, games

def pitcher_yrfi_rate(df, name, before_date):
    games = df[(df["name"] == name) & (df["date"] < before_date)]
    return (games["earned_runs"] > 0).mean() if not games.empty else 0.5

def pitcher_metrics(df):
    ip = df["ip"].sum()
    if ip == 0:
        return 4.5, 8.0
    era = df["earned_runs"].sum() / ip * 9
    k9 = df["strikeouts"].sum() / ip * 9
    return era, k9

def team_yrfi_rate(df, team_col, run_col, team, date):
    games = df[(df[team_col] == team) & (df["date"] < date)].tail(20)
    return (games[run_col] > 0).mean() if not games.empty else 0.5

def get_today_matchups():
    today = datetime.today().strftime("%Y-%m-%d")
    schedule = statsapi.schedule(date=today)

    matchups = []
    for game in schedule:
        if "home_probable_pitcher" not in game or "away_probable_pitcher" not in game:
            continue

        matchup = {
            "game_id": game["game_id"],
            "home_team": game["home_name"],
            "away_team": game["away_name"],
            "home_pitcher": game["home_probable_pitcher"],
            "away_pitcher": game["away_probable_pitcher"],
            "date": pd.to_datetime(today)
        }
        matchups.append(matchup)
    return pd.DataFrame(matchups)

def predict_today():
    print("📅 Predicting today's NRFI/YRFI and Strikeouts...\n")

    pitchers, games = get_historical_data()
    matchups = get_today_matchups()

    if matchups.empty:
        print("🚫 No games with confirmed pitchers today.")
        return

    predictions = []

    for _, row in matchups.iterrows():
        date = row["date"]
        hp = row["home_pitcher"]
        ap = row["away_pitcher"]

        home_p_stats = pitchers[(pitchers["name"] == hp) & (pitchers["date"] < date)]
        away_p_stats = pitchers[(pitchers["name"] == ap) & (pitchers["date"] < date)]

        home_era, home_k9 = pitcher_metrics(home_p_stats)
        away_era, away_k9 = pitcher_metrics(away_p_stats)

        home_pitcher_yrfi = pitcher_yrfi_rate(pitchers, hp, date)
        away_pitcher_yrfi = pitcher_yrfi_rate(pitchers, ap, date)

        home_team_rate = team_yrfi_rate(games, "home_team", "home_1st_runs", row["home_team"], date)
        away_team_rate = team_yrfi_rate(games, "away_team", "away_1st_runs", row["away_team"], date)

        features = pd.DataFrame([{
            "home_pitcher_era": home_era,
            "home_pitcher_k9": home_k9,
            "away_pitcher_era": away_era,
            "away_pitcher_k9": away_k9,
            "home_pitcher_yrfi_rate": home_pitcher_yrfi,
            "away_pitcher_yrfi_rate": away_pitcher_yrfi,
            "home_team_yrfi_rate": home_team_rate,
            "away_team_yrfi_rate": away_team_rate
        }])

        yrfi_prob = model.predict_proba(features)[0][1]
        hp_ks = round(home_k9 * 5.5 / 9, 1)
        ap_ks = round(away_k9 * 5.5 / 9, 1)

        predictions.append({
            "matchup": f"{row['away_team']} @ {row['home_team']}",
            "home_pitcher": hp,
            "away_pitcher": ap,
            "yrfi_prob": round(yrfi_prob, 3),
            "home_k_proj": hp_ks,
            "away_k_proj": ap_ks
        })

    df = pd.DataFrame(predictions)
    print(df.to_string(index=False))

if __name__ == "__main__":
    predict_today()
