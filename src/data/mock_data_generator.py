# src/data/mock_data_generator.py
# Purpose: Generate realistic mock Meta Ads campaign data
# and write it to Supabase raw_campaigns table

import os
import random
from datetime import date, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from faker import Faker

# ── Setup ──────────────────────────────────────────────
load_dotenv()
fake = Faker()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ── Campaign Definitions ───────────────────────────────
# These mirror real Meta Ads campaign structures
CAMPAIGNS = [
    {
        "campaign_id": "camp_001",
        "campaign_name": "Summer Sale 2025 — Conversions",
        "adsets": [
            {"adset_id": "adset_001", "adset_name": "Lookalike 1% — Purchase"},
            {"adset_id": "adset_002", "adset_name": "Retargeting — Cart Abandon"},
            {"adset_id": "adset_003", "adset_name": "Interest — Fitness 25-34"},
        ]
    },
    {
        "campaign_id": "camp_002",
        "campaign_name": "Brand Awareness Q2 — Reach",
        "adsets": [
            {"adset_id": "adset_004", "adset_name": "Broad — 18-45 India"},
            {"adset_id": "adset_005", "adset_name": "Lookalike 3% — Page Fans"},
        ]
    },
    {
        "campaign_id": "camp_003",
        "campaign_name": "Product Launch — App Installs",
        "adsets": [
            {"adset_id": "adset_006", "adset_name": "Interest — Tech Enthusiasts"},
            {"adset_id": "adset_007", "adset_name": "Retargeting — Website Visitors 30d"},
            {"adset_id": "adset_008", "adset_name": "Lookalike 2% — High LTV"},
        ]
    }
]

# ── Data Generator Function ────────────────────────────
def generate_campaign_data(scenario="normal"):
    """
    Generate one day of campaign metrics for all ad sets.
    
    scenario options:
    - "normal"      → healthy performing campaigns
    - "problematic" → some campaigns underperforming
    - "mixed"       → mix of good and bad performance
    """
    
    records = []
    today = date.today()

    for campaign in CAMPAIGNS:
        for adset in campaign["adsets"]:

            # Base metrics — normal healthy campaign
            impressions = random.randint(8000, 25000)
            
            # Scenario logic — this is where we simulate problems
            if scenario == "problematic":
                # Simulate bad performance for testing anomaly detection
                clicks = random.randint(50, 150)        # Very low CTR
                spend = round(random.uniform(200, 500), 2)
                conversions = random.randint(0, 2)      # Almost no conversions
                roas = round(random.uniform(0.3, 0.8), 2)  # ROAS below 1 = losing money

            elif scenario == "mixed":
                # Some good, some bad
                if adset["adset_id"] in ["adset_002", "adset_005", "adset_007"]:
                    # These specific adsets perform badly
                    clicks = random.randint(50, 150)
                    spend = round(random.uniform(200, 500), 2)
                    conversions = random.randint(0, 2)
                    roas = round(random.uniform(0.3, 0.8), 2)
                else:
                    # Rest perform normally
                    clicks = random.randint(400, 1200)
                    spend = round(random.uniform(50, 200), 2)
                    conversions = random.randint(10, 40)
                    roas = round(random.uniform(2.5, 6.0), 2)

            else:
                # Normal healthy performance
                clicks = random.randint(400, 1200)
                spend = round(random.uniform(50, 200), 2)
                conversions = random.randint(10, 40)
                roas = round(random.uniform(2.5, 6.0), 2)

            # Build the record — matches raw_campaigns table exactly
            record = {
                "campaign_id": campaign["campaign_id"],
                "campaign_name": campaign["campaign_name"],
                "adset_id": adset["adset_id"],
                "adset_name": adset["adset_name"],
                "impressions": impressions,
                "clicks": clicks,
                "spend": spend,
                "conversions": conversions,
                "roas": roas,
                "date_pulled": str(today)
            }

            records.append(record)

    return records


# ── Write to Supabase Function ─────────────────────────
def write_to_supabase(records):
    """
    Write generated records to raw_campaigns table in Supabase
    """
    print(f"\n📤 Writing {len(records)} records to Supabase...")

    response = supabase.table("raw_campaigns").insert(records).execute()

    print(f"✅ Successfully written {len(records)} records!")
    print(f"📅 Date: {records[0]['date_pulled']}")
    print(f"📊 Campaigns covered: {len(CAMPAIGNS)}")
    print(f"📱 Ad sets covered: {len(records)}")
    return response


# ── Generate 7 Days of Historical Data ────────────────
def generate_historical_data():
    """
    Generate 7 days of past data so our anomaly detection
    model has a baseline to compare against.
    Without historical data, the model has nothing to compare to.
    """
    print("🕐 Generating 7 days of historical data...")
    
    today = date.today()
    all_records = []

    for days_ago in range(7, 0, -1):
        past_date = today - timedelta(days=days_ago)
        
        for campaign in CAMPAIGNS:
            for adset in campaign["adsets"]:
                impressions = random.randint(8000, 25000)
                clicks = random.randint(400, 1200)
                spend = round(random.uniform(50, 200), 2)
                conversions = random.randint(10, 40)
                roas = round(random.uniform(2.5, 6.0), 2)

                record = {
                    "campaign_id": campaign["campaign_id"],
                    "campaign_name": campaign["campaign_name"],
                    "adset_id": adset["adset_id"],
                    "adset_name": adset["adset_name"],
                    "impressions": impressions,
                    "clicks": clicks,
                    "spend": spend,
                    "conversions": conversions,
                    "roas": roas,
                    "date_pulled": str(past_date)
                }
                all_records.append(record)

    print(f"📦 Generated {len(all_records)} historical records")
    return all_records


# ── Main Execution ─────────────────────────────────────
if __name__ == "__main__":
    
    print("🚀 Mock Data Generator Starting...")
    print("=" * 50)

    # Step 1 — Generate 7 days of healthy historical data
    # This gives the anomaly model a baseline to learn from
    historical = generate_historical_data()
    write_to_supabase(historical)

    print("\n" + "=" * 50)

    # Step 2 — Generate today's MIXED data
    # Some campaigns performing badly → anomaly detector will flag these
    todays_data = generate_campaign_data(scenario="mixed")
    write_to_supabase(todays_data)

    print("\n" + "=" * 50)
    print("✅ ALL DONE! Check your Supabase raw_campaigns table.")
    print("You should see 64 total records (56 historical + 8 today)")