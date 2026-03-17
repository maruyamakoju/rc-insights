# rc-insights

> Python SDK, CLI, and AI-powered analyzer for RevenueCat Charts API v2.

**rc-insights** gives you a clean Python interface to [RevenueCat's Charts API](https://www.revenuecat.com/docs/api-v2), plus a CLI, an HTML report generator, and **AI-powered strategic analysis** via Claude. Built for indie developers, growth teams, and AI agents that need programmatic access to subscription metrics.

**[Live Demo](https://maruyamakoju.github.io/rc-insights/)** — Interactive report generated from real app data.

## Features

- **Python SDK** — Clean, typed client for all 21 chart endpoints + overview metrics
- **CLI** — `rc-insights overview`, `rc-insights chart mrr`, `rc-insights report`
- **AI Analysis** — `rc-insights analyze` sends your data to Claude for strategic recommendations
- **HTML Reports** — Beautiful, interactive subscription health reports with Plotly charts
- **Auto-insights** — Automatic trend analysis, churn alerts, and conversion benchmarks
- **Rate-limit handling** — Built-in retry with exponential backoff

## Quick Start

### Installation

```bash
pip install rc-insights
```

### Python SDK

```python
from rc_insights import RCInsights

rc = RCInsights(api_key="sk_...", project_id="proj...")

# Get current metrics at a glance
overview = rc.overview()
print(f"MRR: {overview['mrr'].formatted_value}")
print(f"Active Subs: {overview['active_subscriptions'].formatted_value}")

# Fetch MRR trend
mrr = rc.chart("mrr", start_date="2024-01-01", end_date="2024-12-31", resolution="month")
for date, value in mrr.to_series():
    print(f"  {date}: ${value:,.2f}")

# Segmented analysis
revenue_by_country = rc.chart("revenue", start_date="2024-01-01",
                               end_date="2024-12-31", segment="country")
```

### CLI

```bash
export REVENUECAT_API_KEY=sk_...
export REVENUECAT_PROJECT_ID=proj...

# Current metrics
rc-insights overview

# Chart data
rc-insights chart mrr --start 2024-01-01 --end 2024-12-31

# Generate HTML report
rc-insights report --start 2024-01-01 --end 2024-12-31 -o my_report.html
```

### Generate a Health Report

```python
from rc_insights import RCInsights
from rc_insights.report import generate_report

with RCInsights(api_key="sk_...", project_id="proj...") as rc:
    overview = rc.overview()
    charts = rc.health_snapshot(start_date="2024-01-01", end_date="2024-12-31")
    html = generate_report(overview, charts, "2024-01-01", "2024-12-31")

with open("report.html", "w") as f:
    f.write(html)
```

## AI-Powered Analysis

Get strategic recommendations from Claude based on your actual subscription data:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
rc-insights analyze --start 2024-01-01 --end 2024-12-31
```

Claude analyzes your MRR trends, churn patterns, trial conversion, LTV, and more — then returns actionable recommendations like a senior growth advisor would.

```python
from rc_insights import RCInsights
from rc_insights.analyzer import analyze_subscription_health

with RCInsights(api_key="sk_...", project_id="proj...") as rc:
    overview = rc.overview()
    charts = rc.health_snapshot(start_date="2024-01-01", end_date="2024-12-31")
    analysis = analyze_subscription_health(overview, charts, "2024-01-01", "2024-12-31")
    print(analysis)
```

## Supported Charts (21 total)

| Category | Charts |
|----------|--------|
| Revenue | `revenue`, `mrr`, `mrr_movement`, `arr` |
| Lifetime Value | `ltv_per_customer`, `ltv_per_paying_customer` |
| Active Subscriptions | `actives`, `actives_movement`, `actives_new` |
| Trials | `trials`, `trials_movement`, `trials_new` |
| Conversion | `conversion_to_paying`, `trial_conversion_rate`, `customers_new` |
| Churn & Retention | `churn`, `subscription_retention`, `refund_rate` |
| Other | `subscription_status`, `cohort_explorer`, `customers_active` |

## Filtering & Segmentation

```python
# Segment by country
rc.chart("revenue", segment="country", start_date="2024-01-01", end_date="2024-12-31")

# Filter to specific store
rc.chart("mrr", filters={"store": "app_store"}, start_date="2024-01-01", end_date="2024-12-31")

# Check available options
options = rc.chart_options("revenue")
print(options.filters)   # Available filter dimensions
print(options.segments)  # Available segment dimensions
```

## Report Features

The HTML report includes:

- **Overview cards** — MRR, active subs, trials, revenue at a glance
- **Interactive charts** — MRR trend, revenue, churn rate, active subs, trial conversion, LTV
- **Auto-generated insights** — Trend analysis, churn warnings, conversion benchmarks
- **Dark theme** — Easy on the eyes, great for presentations

## Development

```bash
git clone https://github.com/maruyamakoju/rc-insights.git
cd rc-insights
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT

---

Built by [@maruyamakoju](https://github.com/maruyamakoju) (operated by Claude Agent) for the RevenueCat developer community.
