"""RevenueCat Charts API v2 client."""

from __future__ import annotations

import time
from typing import Any, Optional

import httpx

from rc_insights.models import ChartData, ChartOptions, OverviewMetrics

# All 21 chart names supported by the API
CHART_NAMES = [
    "revenue", "mrr", "mrr_movement", "arr",
    "ltv_per_customer", "ltv_per_paying_customer",
    "actives", "actives_movement", "actives_new",
    "trials", "trials_movement", "trials_new",
    "conversion_to_paying", "trial_conversion_rate", "customers_new",
    "churn", "subscription_retention", "refund_rate",
    "subscription_status", "cohort_explorer", "customers_active",
]

# Resolution mapping: human-readable -> API integer
RESOLUTIONS = {"day": 0, "week": 1, "month": 2, "quarter": 3, "year": 4}


class RCInsightsError(Exception):
    """Base exception for rc-insights."""
    pass


class APIError(RCInsightsError):
    """Raised when the API returns an error response."""
    def __init__(self, status_code: int, message: str, detail: Any = None):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {message}")


class RateLimitError(APIError):
    """Raised when rate-limited (HTTP 429)."""
    pass


class RCInsights:
    """Client for RevenueCat Charts API v2.

    Usage::

        from rc_insights import RCInsights

        rc = RCInsights(api_key="sk_...", project_id="proj...")
        overview = rc.overview()
        mrr = rc.chart("mrr", start_date="2024-01-01", end_date="2024-12-31")
    """

    BASE_URL = "https://api.revenuecat.com/v2"

    def __init__(
        self,
        api_key: str,
        project_id: str,
        *,
        timeout: float = 30.0,
        max_retries: int = 2,
        retry_delay: float = 5.0,
    ):
        self.project_id = project_id
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            },
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "RCInsights":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ----- internal -----

    def _request(self, method: str, path: str, params: Optional[dict] = None) -> dict:
        """Make an HTTP request with retry on rate-limit."""
        url = f"/projects/{self.project_id}{path}"
        for attempt in range(self._max_retries + 1):
            resp = self._client.request(method, url, params=params)
            if resp.status_code == 429:
                if attempt < self._max_retries:
                    time.sleep(self._retry_delay * (attempt + 1))
                    continue
                raise RateLimitError(429, "Rate limit exceeded after retries")
            if resp.status_code >= 400:
                try:
                    body = resp.json()
                    msg = body.get("message", resp.text[:200])
                except Exception:
                    msg = resp.text[:200]
                raise APIError(resp.status_code, msg)
            return resp.json()
        raise RCInsightsError("Unexpected retry exhaustion")

    # ----- public API -----

    def overview(self) -> OverviewMetrics:
        """Get overview metrics (MRR, active subs, trials, etc.)."""
        data = self._request("GET", "/metrics/overview")
        return OverviewMetrics.from_dict(data)

    def chart(
        self,
        chart_name: str,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        resolution: str = "month",
        segment: Optional[str] = None,
        revenue_type: Optional[str] = None,
        filters: Optional[dict[str, str]] = None,
    ) -> ChartData:
        """Fetch chart time-series data.

        Args:
            chart_name: One of the 21 supported chart names (e.g. "mrr", "revenue").
            start_date: Start date as YYYY-MM-DD string.
            end_date: End date as YYYY-MM-DD string.
            resolution: One of "day", "week", "month", "quarter", "year".
            segment: Segment dimension (e.g. "country", "platform").
            revenue_type: "revenue", "revenue_net_of_taxes", or "proceeds".
            filters: Dict of filter_id -> value (e.g. {"country": "US"}).

        Returns:
            ChartData with parsed time-series values.
        """
        if chart_name not in CHART_NAMES:
            raise ValueError(
                f"Unknown chart '{chart_name}'. Valid: {', '.join(CHART_NAMES)}"
            )

        params: dict[str, Any] = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if resolution in RESOLUTIONS:
            params["resolution"] = RESOLUTIONS[resolution]
        if segment:
            params["segment"] = segment
        if revenue_type:
            params["revenue_type"] = revenue_type
        if filters:
            for k, v in filters.items():
                params[f"filter[{k}]"] = v

        data = self._request("GET", f"/charts/{chart_name}", params=params)
        return ChartData.from_dict(data, chart_name=chart_name)

    def chart_options(self, chart_name: str) -> ChartOptions:
        """Get available filters, segments, and resolutions for a chart."""
        if chart_name not in CHART_NAMES:
            raise ValueError(f"Unknown chart '{chart_name}'.")
        data = self._request("GET", f"/charts/{chart_name}/options")
        return ChartOptions.from_dict(data)

    def health_snapshot(
        self,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        resolution: str = "month",
    ) -> dict[str, ChartData]:
        """Fetch key health charts in one call.

        Returns a dict with keys: mrr, revenue, churn, actives,
        trial_conversion_rate, ltv_per_paying_customer.
        """
        key_charts = [
            "mrr", "revenue", "churn", "actives",
            "trial_conversion_rate", "ltv_per_paying_customer",
        ]
        results = {}
        for name in key_charts:
            try:
                results[name] = self.chart(
                    name,
                    start_date=start_date,
                    end_date=end_date,
                    resolution=resolution,
                )
            except APIError:
                continue  # skip unavailable charts
        return results
