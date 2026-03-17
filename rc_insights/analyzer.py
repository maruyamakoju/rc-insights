"""AI-powered subscription analytics using Claude API."""

from __future__ import annotations

import json
import os
from datetime import date
from typing import Optional

import httpx

from rc_insights.models import ChartData, OverviewMetrics


SYSTEM_PROMPT = """You are a senior subscription business analyst and growth strategist.
You analyze RevenueCat Charts API data for subscription apps and provide actionable,
data-driven recommendations.

Your analysis should cover:
1. **Executive Summary** — 2-3 sentence overview of the app's subscription health
2. **Revenue Analysis** — MRR trends, growth rate, revenue per subscriber
3. **Retention & Churn** — Churn patterns, retention signals, warning signs
4. **Growth Metrics** — New customers, trial conversion, acquisition momentum
5. **Lifetime Value** — LTV trends and what they imply about product-market fit
6. **Strategic Recommendations** — 3-5 specific, actionable next steps with expected impact

Be specific with numbers. Reference actual data points. Don't be generic.
If you see concerning trends, say so directly. If something is going well, say why it matters.
Think like you're advising the founder of this app in a 1:1 meeting."""


def _format_chart_for_prompt(name: str, chart: ChartData) -> str:
    """Format chart data as a compact string for the LLM prompt."""
    series = chart.to_series()
    if not series:
        return f"  {name}: no data"

    unit = chart.measures[0].unit if chart.measures else ""
    prefix = "$" if unit == "$" else ""
    suffix = "%" if unit == "%" else ""

    # Show first, last, min, max, and trend
    values = [v for _, v in series]
    first_date, first_val = series[0]
    last_date, last_val = series[-1]
    avg_val = sum(values) / len(values)
    min_val = min(values)
    max_val = max(values)

    if first_val > 0:
        change_pct = ((last_val - first_val) / first_val) * 100
    else:
        change_pct = 0

    lines = [
        f"  {chart.display_name} ({chart.resolution}, {len(series)} periods):",
        f"    Range: {first_date} to {last_date}",
        f"    First: {prefix}{first_val:,.2f}{suffix} → Last: {prefix}{last_val:,.2f}{suffix} ({change_pct:+.1f}%)",
        f"    Avg: {prefix}{avg_val:,.2f}{suffix} | Min: {prefix}{min_val:,.2f}{suffix} | Max: {prefix}{max_val:,.2f}{suffix}",
    ]

    # Add recent 3 months for trend visibility
    recent = series[-3:] if len(series) >= 3 else series
    recent_str = ", ".join(f"{d}: {prefix}{v:,.2f}{suffix}" for d, v in recent)
    lines.append(f"    Recent: {recent_str}")

    return "\n".join(lines)


def _format_overview_for_prompt(overview: OverviewMetrics) -> str:
    """Format overview metrics for the LLM prompt."""
    lines = ["  Current Overview (point-in-time):"]
    for m in overview.metrics:
        lines.append(f"    {m.name}: {m.formatted_value} ({m.period})")
    return "\n".join(lines)


def build_analysis_prompt(
    overview: OverviewMetrics,
    charts: dict[str, ChartData],
    start_date: str,
    end_date: str,
) -> str:
    """Build the full analysis prompt with all data."""
    sections = [
        f"Subscription App Analytics Data ({start_date} to {end_date})",
        "=" * 60,
        "",
        _format_overview_for_prompt(overview),
        "",
        "Historical Trends:",
    ]

    chart_order = [
        "mrr", "revenue", "churn", "actives",
        "trial_conversion_rate", "ltv_per_paying_customer",
        "actives_new", "trials", "customers_new",
    ]
    for name in chart_order:
        if name in charts:
            sections.append(_format_chart_for_prompt(name, charts[name]))
            sections.append("")

    sections.append("Please provide your comprehensive analysis and strategic recommendations.")

    return "\n".join(sections)


def analyze_with_claude(
    prompt: str,
    *,
    api_key: Optional[str] = None,
    model: str = "claude-sonnet-4-20250514",
) -> str:
    """Send analysis prompt to Claude API and return the response."""
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError(
            "Set ANTHROPIC_API_KEY environment variable or pass api_key parameter. "
            "Get your key at: https://console.anthropic.com/settings/keys"
        )

    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 4096,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120.0,
    )

    if resp.status_code != 200:
        raise RuntimeError(f"Claude API error {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    content = data.get("content", [])
    if content and content[0].get("type") == "text":
        return content[0]["text"]
    return "No analysis generated."


def analyze_subscription_health(
    overview: OverviewMetrics,
    charts: dict[str, ChartData],
    start_date: str,
    end_date: str,
    *,
    anthropic_api_key: Optional[str] = None,
    model: str = "claude-sonnet-4-20250514",
) -> str:
    """Run full AI analysis on subscription data.

    Returns a markdown-formatted strategic analysis.
    """
    prompt = build_analysis_prompt(overview, charts, start_date, end_date)
    return analyze_with_claude(prompt, api_key=anthropic_api_key, model=model)
