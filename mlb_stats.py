import statsapi
import json
import datetime
import os
import time

def get_daily_mlb_games(date_str):
    games = statsapi.schedule(date=date_str, sportId=1)
    results = []

    for game in games:
        summary = {
            "date": date_str,
            "home_team": game["home_name"],
            "away_team": game["away_name"],
            "home_score": game.get("home_score", None),
            "away_score": game.get("away_score", None),
            "status": game["status"],
            "game_id": game["game_id"],
            "starting_pitchers": {
                "home": game.get("home_probable_pitcher", "Unknown"),
                "away": game.get("away_probable_pitcher", "Unknown")
            }
        }

        # Get 1st inning runs
        try:
            linescore = statsapi.get("game_linescore", {"gamePk": game["game_id"]})
            if linescore.get("innings"):
                summary["first_inning_runs"] = {
                    "home": linescore["innings"][0].get("home", {}).get("runs", 0),
                    "away": linescore["innings"][0].get("away", {}).get("runs", 0)
                }
            else:
                summary["first_inning_runs"] = {"home": 0, "away": 0}
        except Exception:
            summary["first_inning_runs"] = {"home": 0, "away": 0}

        # Get boxscore data
        try:
            boxscore = statsapi.get("game_boxscore", {"gamePk": game["game_id"]})
            home_players = boxscore["teams"]["home"]["players"]
            away_players = boxscore["teams"]["away"]["players"]
            players = {**home_players, **away_players}

            # Batting stats
            player_stats = []
            for pid, pdata in players.items():
                stats = pdata.get("stats", {}).get("batting", {})
                if stats.get("atBats", 0) > 0:
                    player_stats.append({
                        "name": pdata.get("person", {}).get("fullName", "Unknown"),
                        "team": pdata.get("parentTeamName", "Unknown"),
                        "hits": stats.get("hits", 0),
                        "rbi": stats.get("rbi", 0)
                    })

            # Pitching stats
            pitcher_stats = []
            for pid, pdata in players.items():
                stats = pdata.get("stats", {}).get("pitching", {})
                if stats.get("inningsPitched"):
                    pitcher_stats.append({
                        "name": pdata.get("person", {}).get("fullName", "Unknown"),
                        "team": pdata.get("parentTeamName", "Unknown"),
                        "innings_pitched": stats.get("inningsPitched", "0.0"),
                        "strikeouts": stats.get("strikeOuts", 0),
                        "earned_runs": stats.get("earnedRuns", 0)
                    })

            summary["player_stats"] = player_stats
            summary["pitcher_stats"] = pitcher_stats

        except Exception:
            summary["player_stats"] = []
            summary["pitcher_stats"] = []

        results.append(summary)

    return results

def get_date_range(start_date, end_date):
    current = start_date
    while current <= end_date:
        yield current.strftime('%Y-%m-%d')
        current += datetime.timedelta(days=1)

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    start = datetime.date(2022, 5, 2)
    end = datetime.date(2025, 7, 6)

    for date_str in get_date_range(start, end):
        file_path = f"data/mlb_games_{date_str}.json"

        if os.path.exists(file_path):
            print(f"⏭️ {date_str}: already exists, skipping.")
            continue

        try:
            daily_games = get_daily_mlb_games(date_str)
            if not daily_games:
                print(f"📭 {date_str}: no games.")
                continue

            with open(file_path, "w") as f:
                json.dump(daily_games, f, indent=2)

            print(f"✅ {date_str}: saved {len(daily_games)} games.")

        except Exception as e:
            print(f"❌ {date_str}: error - {e}")

        time.sleep(1)  # prevent rate-limiting
