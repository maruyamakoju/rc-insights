"""Tests for rc_insights.models."""

import datetime as dt

from rc_insights.models import (
    ChartData,
    DataPoint,
    Measure,
    OverviewMetric,
    OverviewMetrics,
    ChartOptions,
    FilterOption,
)


def test_overview_metric_from_dict():
    d = {
        "id": "mrr",
        "name": "MRR",
        "description": "In the last 28 days",
        "value": 4557.0,
        "unit": "$",
        "period": "P28D",
    }
    m = OverviewMetric.from_dict(d)
    assert m.id == "mrr"
    assert m.value == 4557.0
    assert m.formatted_value == "$4,557.00"


def test_overview_metric_formatted_count():
    m = OverviewMetric(id="active_trials", name="Active Trials",
                       description="", value=65, unit="#", period="P0D")
    assert m.formatted_value == "65"


def test_overview_metric_formatted_pct():
    m = OverviewMetric(id="churn", name="Churn", description="",
                       value=5.3, unit="%", period="P28D")
    assert m.formatted_value == "5.3%"


def test_overview_metrics_get():
    metrics = OverviewMetrics(metrics=[
        OverviewMetric(id="mrr", name="MRR", description="",
                       value=1000, unit="$", period="P28D"),
        OverviewMetric(id="actives", name="Active", description="",
                       value=200, unit="#", period="P0D"),
    ])
    assert metrics.get("mrr").value == 1000
    assert metrics.get("nonexistent") is None
    assert metrics["actives"].value == 200


def test_chart_data_from_dict():
    d = {
        "display_name": "MRR",
        "category": "revenue",
        "description": "Monthly Recurring Revenue",
        "resolution": "month",
        "start_date": 1704067200,  # 2024-01-01
        "end_date": 1735689600,    # 2024-12-31
        "measures": [
            {"display_name": "MRR", "unit": "$", "description": "", "decimal_precision": 2}
        ],
        "values": [
            {"cohort": 1704067200, "measure": 0, "value": 1000.0, "incomplete": False},
            {"cohort": 1706745600, "measure": 0, "value": 1100.0, "incomplete": False},
            {"cohort": 1709251200, "measure": 0, "value": 1200.0, "incomplete": True},
        ],
        "summary": {"average": {"MRR": 1100.0}, "total": {"MRR": 3300.0}},
        "segments": None,
    }
    chart = ChartData.from_dict(d, chart_name="mrr")
    assert chart.name == "mrr"
    assert chart.display_name == "MRR"
    assert len(chart.values) == 3
    assert len(chart.measures) == 1

    # to_series excludes incomplete
    series = chart.to_series()
    assert len(series) == 2
    assert series[0][1] == 1000.0
    assert series[1][1] == 1100.0


def test_chart_data_to_dict_series():
    d = {
        "display_name": "Revenue",
        "category": "revenue",
        "description": "",
        "resolution": "month",
        "start_date": 1704067200,
        "end_date": 1706745600,
        "measures": [{"display_name": "Revenue", "unit": "$"}],
        "values": [
            {"cohort": 1704067200, "measure": 0, "value": 500.0, "incomplete": False},
        ],
        "summary": {},
        "segments": None,
    }
    chart = ChartData.from_dict(d, chart_name="revenue")
    ds = chart.to_dict_series()
    assert len(ds["dates"]) == 1
    assert ds["values"][0] == 500.0


def test_chart_options_from_dict():
    d = {
        "filters": [
            {"id": "country", "display_name": "Country", "values": [{"id": "US", "display_name": "United States"}]},
        ],
        "segments": [{"id": "country", "display_name": "Country"}],
        "resolutions": [{"id": 0, "display_name": "Day"}],
    }
    opts = ChartOptions.from_dict(d)
    assert len(opts.filters) == 1
    assert opts.filters[0].id == "country"
    assert len(opts.segments) == 1
