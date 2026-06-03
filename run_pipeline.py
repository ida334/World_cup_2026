"""
One-command pipeline runner.

Usage:
    python run_pipeline.py                   # full run
    python run_pipeline.py --skip-db         # skip CSV→SQLite step
    python run_pipeline.py --skip-train      # skip model training
    python run_pipeline.py --skip-sim        # skip Monte Carlo simulation
"""
import argparse
import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def main():
    parser = argparse.ArgumentParser(description="World Cup 2026 pipeline")
    parser.add_argument("--skip-db",    action="store_true", help="Skip database build")
    parser.add_argument("--skip-train", action="store_true", help="Skip model training")
    parser.add_argument("--skip-sim",   action="store_true", help="Skip simulation")
    args = parser.parse_args()

    t0 = time.time()

    # ── Phase 1: Build database ───────────────────────────────────────────────
    if not args.skip_db:
        print("\n[1/3] Building SQLite database from CSV files...")
        from src.db_loader import build_database
        build_database(force_rebuild=True)
    else:
        print("[1/3] Skipping database build (--skip-db)")

    # ── Phase 2: Train model ──────────────────────────────────────────────────
    if not args.skip_train:
        print("\n[2/3] Training XGBoost model...")
        from src.db_loader import get_connection
        from src.model import train_model
        conn = get_connection()
        model = train_model(conn, save=True)
        conn.close()
    else:
        print("[2/3] Skipping model training (--skip-train)")

    # ── Phase 3: Run simulation ───────────────────────────────────────────────
    if not args.skip_sim:
        print("\n[3/3] Running Monte Carlo simulation (10,000 iterations)...")
        from src.db_loader import get_connection
        from src.model import load_model
        from src.simulator import run_full_simulation, save_simulation, get_top_predictions

        conn  = get_connection()
        model = load_model()
        results = run_full_simulation(model, conn)
        save_simulation(results)
        conn.close()

        print("\n  Top 10 championship contenders:")
        for row in get_top_predictions(results, n=10):
            print(f"    {row['team']:<20} winner={row['winner']:.1%}  "
                  f"final={row['final']:.1%}  sf={row['sf']:.1%}")
    else:
        print("[3/3] Skipping simulation (--skip-sim)")

    elapsed = time.time() - t0
    print(f"\nPipeline complete in {elapsed:.1f}s")
    print("\nReady. Launch the dashboard with:")
    print("  python -m streamlit run dashboard/app.py")


if __name__ == "__main__":
    main()
