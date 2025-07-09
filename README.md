
# ⚾ MLB NRFI Prediction Project

This project builds a machine learning pipeline to predict **No Runs First Inning (NRFI)** and **Yes Runs First Inning (YRFI)** outcomes for MLB games, using historical data, player statistics, and real-time matchups.

---

## 📁 Project Structure

```
mlb_project/
├── data/                         # Daily scraped JSON files
├── models/                       # Trained models & feature sets
├── logs/                         # Daily prediction logs
├── mlb_stats.db                  # SQLite database of games
├── nrfi_model.py                 # Feature engineering from DB
├── nrfi_model_train.py           # Model training script
├── predict_today_live.py         # Predicts today’s games
├── load_db_enhanced.py           # Loads game JSONs into DB
├── update_boxscore_hr_tb.py      # Updates hitters with HR & TB
├── requirements.txt              # (Optional) Python dependencies
└── README.md                     # You're here
```

---

## 🧠 Project Workflow

### 1. 🔄 Scrape and Save JSON Game Data
Use your scraper to store each day's games to `data/mlb_games_YYYY-MM-DD.json`.

### 2. 🏗️ Load Game Data into the Database
Run:
```bash
python load_db_enhanced.py
```

### 3. 🔁 Update Hitter Stats (HR + Total Bases)
Run:
```bash
python update_boxscore_hr_tb.py
```

### 4. 🧮 Generate Features from DB
Run:
```bash
python nrfi_model.py
```

This creates `nrfi_features_enhanced.csv` with historical features.

### 5. 🧠 Train the Model
Run:
```bash
python nrfi_model_train.py
```

Saves `nrfi_model.pkl` to `models/`.

### 6. 📊 Predict Today’s Games
Run:
```bash
python predict_today_live.py
```

Outputs predictions to `logs/daily_predictions_log.csv`.

---

## 🔍 Features Used

- Pitcher ERA, K/9, and 1st inning ERA
- Team average 1st inning runs (last 10 games)
- Strikeout projections
- Hitter trends: Hits, HRs, RBIs, Total Bases

---

## 💡 Future Improvements

- Compare model to capper lines (Twitter scraping)
- Live game results auto-update
- Advanced hitter metrics (e.g. wOBA, ISO)
- Betting optimization and bankroll tracking

---

## 🛠️ Requirements

Install dependencies:

```bash
pip install pandas scikit-learn statsapi joblib
```

---

## 🤝 Contributing

If you're collaborating with others or planning to deploy as a web app, reach out to coordinate structure, APIs, and model updates.

---

Enjoy building sharp predictive insights on the first inning! ⚾
