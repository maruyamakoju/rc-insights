"""Quick start example for rc-insights."""

import os
from rc_insights import RCInsights

# Set these in your environment, or pass directly
API_KEY = os.environ.get("REVENUECAT_API_KEY", "sk_your_key_here")
PROJECT_ID = os.environ.get("REVENUECAT_PROJECT_ID", "proj_your_id_here")

with RCInsights(api_key=API_KEY, project_id=PROJECT_ID) as rc:
    # 1. Get current overview metrics
    overview = rc.overview()
    for m in overview.metrics:
        print(f"{m.name}: {m.formatted_value}")

    print("\n---\n")

    # 2. Fetch MRR trend (last 12 months)
    mrr = rc.chart("mrr", start_date="2025-01-01", end_date="2025-12-31", resolution="month")
    print(f"MRR Trend ({mrr.resolution}):")
    for date, value in mrr.to_series():
        print(f"  {date}: ${value:,.2f}")

    # 3. Check summary stats
    if mrr.summary:
        print(f"\n  Average: ${mrr.summary.get('average', {}).get('MRR', 0):,.2f}")
        print(f"  Total:   ${mrr.summary.get('total', {}).get('MRR', 0):,.2f}")
