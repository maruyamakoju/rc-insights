"""Generate a full subscription health report."""

import os
from rc_insights import RCInsights
from rc_insights.report import generate_report

API_KEY = os.environ.get("REVENUECAT_API_KEY", "sk_your_key_here")
PROJECT_ID = os.environ.get("REVENUECAT_PROJECT_ID", "proj_your_id_here")

with RCInsights(api_key=API_KEY, project_id=PROJECT_ID) as rc:
    # Fetch overview
    overview = rc.overview()
    print(f"Fetched {len(overview.metrics)} overview metrics")

    # Fetch key charts for the report
    charts = rc.health_snapshot(
        start_date="2024-01-01",
        end_date="2025-12-31",
        resolution="month",
    )
    print(f"Fetched {len(charts)} charts")

    # Generate HTML report
    html = generate_report(overview, charts, "2024-01-01", "2025-12-31")
    output_path = "subscription_health_report.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report saved to {output_path} ({len(html):,} bytes)")
    print("Open it in your browser to view the interactive charts!")
