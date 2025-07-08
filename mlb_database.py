import sqlite3

def create_mlb_db(db_name="mlb_stats.db"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Games table
    c.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            date TEXT,
            home_team TEXT,
            away_team TEXT,
            home_score INTEGER,
            away_score INTEGER,
            home_pitcher TEXT,
            away_pitcher TEXT,
            home_1st_runs INTEGER,
            away_1st_runs INTEGER
        )
    ''')

    # Hitters table
    c.execute('''
        CREATE TABLE IF NOT EXISTS hitters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            name TEXT,
            team TEXT,
            hits INTEGER,
            rbi INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
    ''')

    # Pitchers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS pitchers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            name TEXT,
            team TEXT,
            innings_pitched TEXT,
            strikeouts INTEGER,
            earned_runs INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"✅ Created database '{db_name}' with tables: games, hitters, pitchers")

if __name__ == "__main__":
    create_mlb_db()
