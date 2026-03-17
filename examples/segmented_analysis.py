"""Example: Analyze revenue by country segment."""

import os
import time
from rc_insights import RCInsights

API_KEY = os.environ.get("REVENUECAT_API_KEY", "sk_your_key_here")
PROJECT_ID = os.environ.get("REVENUECAT_PROJECT_ID", "proj_your_id_here")

with RCInsights(api_key=API_KEY, project_id=PROJECT_ID) as rc:
    # Check available segments for revenue chart
    options = rc.chart_options("revenue")
    print("Available segments:")
    for seg in options.segments:
        print(f"  - {seg.get('id', '?')}: {seg.get('display_name', '?')}")

    time.sleep(5)  # Respect rate limit

    # Fetch revenue segmented by country
    revenue = rc.chart(
        "revenue",
        start_date="2025-01-01",
        end_date="2025-12-31",
        resolution="month",
        segment="country",
    )

    print(f"\nRevenue by Country ({revenue.resolution}):")
    if revenue.segments:
        print(f"  Segments found: {', '.join(revenue.segments[:10])}")

    # Show data points with segment info
    for v in revenue.values[:20]:
        seg_label = f" [{v.segment}]" if v.segment else ""
        print(f"  {v.date}: ${v.value:,.2f}{seg_label}")
