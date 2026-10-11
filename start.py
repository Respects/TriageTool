import argparse
import json
import subprocess
import sys
import time
import random
from datetime import date, timedelta
from Data.database import clear_cases
import httpx

WEBHOOK_URL = "http://localhost:5678/webhook/964c2e1a-d01e-4c9c-a27f-70553ef9931f"
API_HEALTH_URL = "http://localhost:8000/docs"
CASES_FILE = "Data/dispute_cases.json"


def realistic_dates(today):
    received = today - timedelta(days=random.randint(0, today.day - 1 if today.day > 1 else 0))
    deadline = today + timedelta(days=random.randint(7, 25))
    return received, deadline


def historical_dates(today):
    received = today - timedelta(days=random.randint(30, 180))
    # deadline always comfortably outside the 7-day window
    deadline = today + timedelta(days=random.randint(21, 60))
    return received, deadline


def seed_cases(strategy):
    with open(CASES_FILE) as f:
        data = json.load(f)

    today = date.today()
    date_fn = historical_dates if strategy == "historical" else realistic_dates

    for case in data["cases"]:
        received, deadline = date_fn(today)
        case["date_received"] = received.isoformat()
        case["response_deadline"] = deadline.isoformat()
        try:
            r = httpx.post(WEBHOOK_URL, json=case, timeout=30.0)
            print(f"  {case['case_id']}: {r.status_code}")
        except httpx.HTTPError as e:
            print(f"  {case['case_id']}: FAILED ({e})")
        time.sleep(1)


def wait_for_api(timeout=30):
    print("Waiting for API to be ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            if httpx.get(API_HEALTH_URL, timeout=2.0).status_code == 200:
                print("API is ready.")
                return True
        except httpx.HTTPError:
            pass
        time.sleep(1)
    print("API did not become ready in time.")
    return False


def main():
    parser = argparse.ArgumentParser(description="Start the triage tool and seed cases.")
    parser.add_argument("--historical", action="store_true",
                        help="Seed with dates spread over past months, deadlines safely distant.")
    parser.add_argument("--clear", action="store_true",
                        help="Clear all cases (and triage log) before seeding.")
    parser.add_argument("--no-seed", action="store_true",
                        help="Start services without seeding any cases.")
    args = parser.parse_args()

    if args.clear:
        print("Clearing database...")
        clear_cases()
        print("Database cleared.")

    print("Starting API...")
    api = subprocess.Popen([sys.executable, "-m", "uvicorn", "api:app", "--port", "8000"])
    print("Starting Streamlit frontend...")
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "triage_frontend.py"],
        cwd="Frontend",
    )

    try:
        if not args.no_seed:
            if wait_for_api():
                strategy = "historical" if args.historical else "realistic"
                print(f"Seeding cases ({strategy})...")
                seed_cases(strategy)
                print("Seeding complete.")

        print("\nServices running. Press Ctrl+C to stop.")
        api.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        api.terminate()
        frontend.terminate()


if __name__ == "__main__":
    main()

