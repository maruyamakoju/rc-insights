"""Tests for rc_insights.client using respx for HTTP mocking."""

import pytest
import httpx
import respx

from rc_insights.client import RCInsights, APIError, RateLimitError, CHART_NAMES


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
    ],
    "summary": {"average": {"MRR": 4100.0}},
    "segments": None,
    "filtering_allowed": True,
    "segmenting_allowed": True,
}


@respx.mock
def test_overview():
    respx.get("https://api.revenuecat.com/v2/projects/proj_test/metrics/overview").mock(
        return_value=httpx.Response(200, json=OVERVIEW_RESPONSE)
    )
    rc = RCInsights(api_key="sk_test", project_id="proj_test")
    overview = rc.overview()
    assert len(overview.metrics) == 2
    assert overview["mrr"].value == 4557.0
    rc.close()


@respx.mock
def test_chart():
    respx.get("https://api.revenuecat.com/v2/projects/proj_test/charts/mrr").mock(
        return_value=httpx.Response(200, json=CHART_RESPONSE)
    )
    rc = RCInsights(api_key="sk_test", project_id="proj_test")
    chart = rc.chart("mrr", start_date="2024-01-01", end_date="2024-12-31")
    assert chart.name == "mrr"
    assert len(chart.to_series()) == 2
    rc.close()


@respx.mock
def test_api_error():
    respx.get("https://api.revenuecat.com/v2/projects/proj_test/metrics/overview").mock(
        return_value=httpx.Response(403, json={"message": "Forbidden"})
    )
    rc = RCInsights(api_key="sk_bad", project_id="proj_test")
    with pytest.raises(APIError) as exc:
        rc.overview()
    assert exc.value.status_code == 403
    rc.close()


@respx.mock
def test_rate_limit_retry():
    route = respx.get("https://api.revenuecat.com/v2/projects/proj_test/metrics/overview")
    route.side_effect = [
        httpx.Response(429, json={"message": "Rate limited"}),
        httpx.Response(200, json=OVERVIEW_RESPONSE),
    ]
    rc = RCInsights(api_key="sk_test", project_id="proj_test", retry_delay=0.1)
    overview = rc.overview()
    assert len(overview.metrics) == 2
    rc.close()


def test_invalid_chart_name():
    rc = RCInsights(api_key="sk_test", project_id="proj_test")
    with pytest.raises(ValueError, match="Unknown chart"):
        rc.chart("invalid_name")
    rc.close()


def test_chart_names_constant():
    assert "mrr" in CHART_NAMES
    assert "revenue" in CHART_NAMES
    assert "churn" in CHART_NAMES
    assert len(CHART_NAMES) == 21
