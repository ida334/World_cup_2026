"""
XGBoost multi-class classifier for World Cup match outcome prediction.
Classes: 0=Home win, 1=Draw, 2=Away win
"""
import os
import sqlite3
import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix

from src.feature_engineering import (
    build_training_matrix, build_prediction_row,
    FEATURE_COLUMNS, LABEL_INV,
)

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "xgb_match_predictor.pkl")


def train_model(conn: sqlite3.Connection, save: bool = True) -> XGBClassifier:
    print("Building feature matrix...")
    X, y, meta = build_training_matrix(conn)
    print(f"  {len(X)} training samples, {X.shape[1]} features")
    print(f"  Label distribution: H={np.sum(y==0)}, D={np.sum(y==1)}, A={np.sum(y==2)}")

    # Class weights to counteract imbalance
    counts = np.bincount(y)
    max_c  = counts.max()
    weights = {i: max_c / c for i, c in enumerate(counts)}

    model = XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.04,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=42,
        verbosity=0,
    )

    # 5-fold stratified cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
    print(f"  CV accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    print(f"  Baseline (always H): {np.sum(y==0)/len(y):.3f}")

    # Fit on full data
    sample_weights = np.array([weights[label] for label in y])
    model.fit(X, y, sample_weight=sample_weights)

    # Feature importance summary
    importances = model.feature_importances_
    ranked = sorted(zip(FEATURE_COLUMNS, importances), key=lambda x: -x[1])
    print("  Top 5 features:")
    for feat, imp in ranked[:5]:
        print(f"    {feat}: {imp:.4f}")

    if save:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        print(f"  Model saved to {MODEL_PATH}")

    return model


def load_model() -> XGBClassifier:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run run_pipeline.py first.")
    return joblib.load(MODEL_PATH)


def predict_match(
    home_team: str,
    away_team: str,
    stage_rank: int,
    conn: sqlite3.Connection,
    model: XGBClassifier | None = None,
) -> dict:
    """
    Returns probability dict and the single most-likely predicted result.
    """
    if model is None:
        model = load_model()
    X = build_prediction_row(home_team, away_team, stage_rank, conn)
    probs = model.predict_proba(X)[0]
    pred  = int(np.argmax(probs))
    return {
        "home_win_prob":   round(float(probs[0]), 4),
        "draw_prob":       round(float(probs[1]), 4),
        "away_win_prob":   round(float(probs[2]), 4),
        "predicted_result": LABEL_INV[pred],
        "home_team":        home_team,
        "away_team":        away_team,
    }


def evaluate_model(conn: sqlite3.Connection, model: XGBClassifier | None = None):
    """Print a full classification report on the training set (for diagnostics)."""
    if model is None:
        model = load_model()
    X, y, meta = build_training_matrix(conn)
    y_pred = model.predict(X)
    print(classification_report(y, y_pred, target_names=["Home win", "Draw", "Away win"]))
    print("Confusion matrix:")
    print(confusion_matrix(y, y_pred))
