"""Tests for rc_insights.analyzer module."""

import pytest
import httpx
import respx

from rc_insights.models import OverviewMetrics, ChartData
from rc_insights.analyzer import (
    build_analysis_prompt,
    _format_chart_for_prompt,
    _format_overview_for_prompt,
    analyze_with_claude,
)


OVERVIEW_RESPONSE = {
    "object": "overview_metrics",
    "metrics": [
        {"id": "mrr", "name": "MRR", "description": "In the last 28 days",
         "object": "overview_metric", "period": "P28D", "unit": "$",
         "value": 4557.0, "last_updated_at": None, "last_updated_at_iso8601": None},
        {"id": "active_subscriptions", "name": "Active Subscriptions",
         "description": "In total", "object": "overview_metric",
         "period": "P0D", "unit": "#", "value": 2529,
         "last_updated_at": None, "last_updated_at_iso8601": None},
    ],
}

CHART_RESPONSE = {
    "object": "chart_data",
    "display_name": "MRR",
    "category": "revenue",
    "description": "Monthly Recurring Revenue",
    "resolution": "month",
    "start_date": 1704067200,
    "end_date": 1735689600,
    "measures": [{"display_name": "MRR", "unit": "$", "description": "", "decimal_precision": 2}],
    "values": [
        {"cohort": 1704067200, "measure": 0, "value": 4000.0, "incomplete": False},
        {"cohort": 1706745600, "measure": 0, "value": 4200.0, "incomplete": False},
        {"cohort": 1709251200, "measure": 0, "value": 4500.0, "incomplete": False},
    ],
    "summary": {"average": {"MRR": 4233.33}},
    "segments": None,
    "filtering_allowed": True,
    "segmenting_allowed": True,
}


def _make_overview():
    return OverviewMetrics.from_dict(OVERVIEW_RESPONSE)


def _make_chart():
    return ChartData.from_dict(CHART_RESPONSE, chart_name="mrr")


def test_format_overview_for_prompt():
    overview = _make_overview()
    text = _format_overview_for_prompt(overview)
    assert "MRR" in text
    assert "$4,557.00" in text
    assert "Active Subscriptions" in text


def test_format_chart_for_prompt():
    chart = _make_chart()
    text = _format_chart_for_prompt("mrr", chart)
    assert "MRR" in text
    assert "$4,000.00" in text
    assert "$4,500.00" in text
    assert "3 periods" in text
    assert "+12.5%" in text  # (4500 - 4000) / 4000 * 100


def test_build_analysis_prompt():
    overview = _make_overview()
    charts = {"mrr": _make_chart()}
    prompt = build_analysis_prompt(overview, charts, "2024-01-01", "2025-12-31")

    assert "2024-01-01 to 2025-12-31" in prompt
    assert "MRR" in prompt
    assert "$4,557.00" in prompt
    assert "strategic recommendations" in prompt.lower()


def test_build_analysis_prompt_empty_charts():
    overview = _make_overview()
    prompt = build_analysis_prompt(overview, {}, "2024-01-01", "2025-12-31")
    assert "MRR" in prompt  # overview still has MRR
    assert "recommendations" in prompt.lower()


@respx.mock
def test_analyze_with_claude():
    respx.post("https://api.anthropic.com/v1/messages").mock(
        return_value=httpx.Response(200, json={
            "content": [{"type": "text", "text": "## Executive Summary\nGreat app!"}],
            "model": "claude-sonnet-4-20250514",
            "role": "assistant",
        })
    )
    result = analyze_with_claude("test prompt", api_key="sk-ant-test")
    assert "Executive Summary" in result
    assert "Great app!" in result


@respx.mock
def test_analyze_with_claude_api_error():
    respx.post("https://api.anthropic.com/v1/messages").mock(
        return_value=httpx.Response(401, json={"error": {"message": "Invalid API key"}})
    )
    with pytest.raises(RuntimeError, match="Claude API error 401"):
        analyze_with_claude("test prompt", api_key="sk-ant-bad")


def test_analyze_with_claude_no_key():
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        analyze_with_claude("test prompt", api_key="")
