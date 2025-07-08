import sqlite3
import json
import os

DB_NAME = "mlb_stats.db"
DATA_FOLDER = "data"

def insert_game(cursor, game):
    def extract_runs(side_data):
        if isinstance(side_data, dict):
            return side_data.get("runs", 0)
        elif isinstance(side_data, int):  # fallback for legacy format
            return side_data
        return 0

    home_data = game.get("first_inning_runs", {}).get("home", {})
    away_data = game.get("first_inning_runs", {}).get("away", {})

    first_inning_home = extract_runs(home_data)
    first_inning_away = extract_runs(away_data)

    cursor.execute('''
        INSERT OR IGNORE INTO games (
            id, date, home_team, away_team,
            home_score, away_score,
            home_pitcher, away_pitcher,
            home_1st_runs, away_1st_runs
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        game["game_id"],
        game["date"],
        game["home_team"],
        game["away_team"],
        game["home_score"],
        game["away_score"],
        game["starting_pitchers"]["home"],
        game["starting_pitchers"]["away"],
        first_inning_home,
        first_inning_away
    ))


def insert_hitters(cursor, game_id, hitters):
    for h in hitters:
        cursor.execute('''
            INSERT INTO hitters (game_id, name, team, hits, rbi)
            VALUES (?, ?, ?, ?, ?)
        ''', (game_id, h["name"], h["team"], h["hits"], h["rbi"]))

def insert_pitchers(cursor, game_id, pitchers):
    for p in pitchers:
        cursor.execute('''
            INSERT INTO pitchers (game_id, name, team, innings_pitched, strikeouts, earned_runs)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (game_id, p["name"], p["team"], p["innings_pitched"], p["strikeouts"], p["earned_runs"]))

def load_all_json_from_folder(folder_path, db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    files = sorted([f for f in os.listdir(folder_path) if f.endswith(".json")])
    total_games = 0

    for filename in files:
        json_path = os.path.join(folder_path, filename)
        try:
            with open(json_path, "r") as f:
                games = json.load(f)

            for game in games:
                insert_game(cur, game)
                insert_hitters(cur, game["game_id"], game.get("player_stats", []))
                insert_pitchers(cur, game["game_id"], game.get("pitcher_stats", []))

            conn.commit()
            print(f"✅ {filename}: {len(games)} games inserted.")
            total_games += len(games)

        except Exception as e:
            print(f"❌ Failed to load {filename}: {e}")

    conn.close()
    print(f"\n📦 Done. Total games inserted: {total_games}")

if __name__ == "__main__":
    load_all_json_from_folder(DATA_FOLDER, DB_NAME)
