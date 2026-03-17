"""Data models for RevenueCat Charts API v2 responses."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Overview metrics
# ---------------------------------------------------------------------------

@dataclass
class OverviewMetric:
    """Single metric from the overview endpoint."""
    id: str
    name: str
    description: str
    value: float
    unit: str
    period: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "OverviewMetric":
        return cls(
            id=d["id"],
            name=d["name"],
            description=d.get("description", ""),
            value=d["value"],
            unit=d.get("unit", ""),
            period=d.get("period", ""),
        )

    @property
    def formatted_value(self) -> str:
        if self.unit == "$":
            return f"${self.value:,.2f}"
        elif self.unit == "%":
            return f"{self.value:.1f}%"
        return f"{self.value:,.0f}"


@dataclass
class OverviewMetrics:
    """Collection of overview metrics."""
    metrics: list[OverviewMetric]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "OverviewMetrics":
        return cls(
            metrics=[OverviewMetric.from_dict(m) for m in d.get("metrics", [])],
        )

    def get(self, metric_id: str) -> Optional[OverviewMetric]:
        for m in self.metrics:
            if m.id == metric_id:
                return m
        return None

    def __getitem__(self, metric_id: str) -> OverviewMetric:
        m = self.get(metric_id)
        if m is None:
            raise KeyError(f"Metric '{metric_id}' not found")
        return m


# ---------------------------------------------------------------------------
# Chart data
# ---------------------------------------------------------------------------

@dataclass
class Measure:
    """Describes one measure axis in a chart."""
    display_name: str
    unit: str
    description: str = ""
    decimal_precision: int = 0

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Measure":
        return cls(
            display_name=d.get("display_name", ""),
            unit=d.get("unit", ""),
            description=d.get("description", ""),
            decimal_precision=d.get("decimal_precision", 0),
        )


@dataclass
class DataPoint:
    """A single value in the chart time-series."""
    date: dt.date
    measure_index: int
    value: float
    incomplete: bool = False
    segment: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict[str, Any], segment: Optional[str] = None) -> "DataPoint":
        ts = d.get("cohort", 0)
        return cls(
            date=dt.date.fromtimestamp(ts),
            measure_index=d.get("measure", 0),
            value=d.get("value", 0.0),
            incomplete=d.get("incomplete", False),
            segment=segment,
        )


@dataclass
class ChartData:
    """Parsed response from the charts endpoint."""
    name: str
    display_name: str
    category: str
    description: str
    resolution: str
    start_date: dt.date
    end_date: dt.date
    measures: list[Measure]
    values: list[DataPoint]
    summary: dict[str, dict[str, float]] = field(default_factory=dict)
    segments: Optional[list[str]] = None

    @classmethod
    def from_dict(cls, d: dict[str, Any], chart_name: str = "") -> "ChartData":
        measures = [Measure.from_dict(m) for m in d.get("measures", [])]

        # Parse segments if present
        seg_list = d.get("segments")
        seg_names: Optional[list[str]] = None
        if seg_list:
            seg_names = [s.get("display_name", f"Segment {i}") for i, s in enumerate(seg_list)]

        # Parse values with segment info
        values: list[DataPoint] = []
        for v in d.get("values", []):
            seg_name = None
            if seg_names and "segment" in v:
                seg_idx = v["segment"]
                if isinstance(seg_idx, int) and seg_idx < len(seg_names):
                    seg_name = seg_names[seg_idx]
            values.append(DataPoint.from_dict(v, segment=seg_name))

        return cls(
            name=chart_name,
            display_name=d.get("display_name", chart_name),
            category=d.get("category", ""),
            description=d.get("description", ""),
            resolution=d.get("resolution", ""),
            start_date=dt.date.fromtimestamp(d.get("start_date", 0)),
            end_date=dt.date.fromtimestamp(d.get("end_date", 0)),
            measures=measures,
            values=values,
            summary=d.get("summary", {}),
            segments=seg_names,
        )

    def to_series(self, measure_index: int = 0) -> list[tuple[dt.date, float]]:
        """Return (date, value) pairs for one measure, excluding incomplete."""
        return [
            (v.date, v.value)
            for v in self.values
            if v.measure_index == measure_index and not v.incomplete
        ]

    def to_dict_series(self, measure_index: int = 0) -> dict[str, list]:
        """Return {dates: [...], values: [...]} for easy plotting."""
        series = self.to_series(measure_index)
        return {
            "dates": [s[0].isoformat() for s in series],
            "values": [s[1] for s in series],
        }


# ---------------------------------------------------------------------------
# Chart options
# ---------------------------------------------------------------------------

@dataclass
class FilterOption:
    """A filter dimension available for a chart."""
    id: str
    display_name: str
    values: list[dict[str, str]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "FilterOption":
        return cls(
            id=d.get("id", ""),
            display_name=d.get("display_name", ""),
            values=d.get("values", []),
        )


@dataclass
class ChartOptions:
    """Available filters, segments, and resolutions for a chart."""
    filters: list[FilterOption]
    segments: list[dict[str, str]]
    resolutions: list[dict[str, Any]]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ChartOptions":
        return cls(
            filters=[FilterOption.from_dict(f) for f in d.get("filters", [])],
            segments=d.get("segments", []),
            resolutions=d.get("resolutions", []),
        )
