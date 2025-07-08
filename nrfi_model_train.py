import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from nrfi_model import load_nrfi_games_with_pitchers

# Load data
df = load_nrfi_games_with_pitchers()

# Fill missing values
df['home_pitcher_era'] = df['home_pitcher_era'].fillna(4.50)
df['away_pitcher_era'] = df['away_pitcher_era'].fillna(4.50)
df['home_pitcher_k9'] = df['home_pitcher_k9'].fillna(8.0)
df['away_pitcher_k9'] = df['away_pitcher_k9'].fillna(8.0)

# Feature set
features = [
    'home_pitcher_era', 'home_pitcher_k9',
    'away_pitcher_era', 'away_pitcher_k9',
    'home_pitcher_yrfi_rate', 'away_pitcher_yrfi_rate',
    'home_team_yrfi_rate', 'away_team_yrfi_rate'
]
X = df[features]
y = df['yrfi']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LogisticRegression(class_weight="balanced", max_iter=1000)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "nrfi_model.pkl")
print("✅ Model saved to nrfi_model.pkl")

# Evaluate
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("📊 Classification Report:")
print(classification_report(y_test, y_pred))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["NRFI", "YRFI"], yticklabels=["NRFI", "YRFI"])
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

# Feature importances
importance = pd.Series(model.coef_[0], index=features)
print("\n🔍 Feature Importance:")
print(importance.sort_values(ascending=False))
