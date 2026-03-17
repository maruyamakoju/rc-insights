"""CLI interface for rc-insights."""

from __future__ import annotations

import json
import os
import sys
from datetime import date, timedelta

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from rc_insights.client import RCInsights, CHART_NAMES, RCInsightsError

console = Console()


def _get_client() -> RCInsights:
    api_key = os.environ.get("REVENUECAT_API_KEY", "")
    project_id = os.environ.get("REVENUECAT_PROJECT_ID", "")
    if not api_key:
        console.print("[red]Error:[/] Set REVENUECAT_API_KEY environment variable.")
        sys.exit(1)
    if not project_id:
        console.print("[red]Error:[/] Set REVENUECAT_PROJECT_ID environment variable.")
        sys.exit(1)
    return RCInsights(api_key=api_key, project_id=project_id)


def _default_dates() -> tuple[str, str]:
    end = date.today()
    start = end - timedelta(days=90)
    return start.isoformat(), end.isoformat()


@click.group()
@click.version_option(package_name="rc-insights")
def cli():
    """rc-insights — RevenueCat Charts API made simple."""
    pass


@cli.command()
def overview():
    """Show current overview metrics (MRR, active subs, trials, etc.)."""
    with _get_client() as rc:
        data = rc.overview()

    table = Table(title="RevenueCat Overview", show_lines=True)
    table.add_column("Metric", style="cyan bold")
    table.add_column("Value", style="green", justify="right")
    table.add_column("Period", style="dim")

    for m in data.metrics:
        table.add_row(m.name, m.formatted_value, m.period)

    console.print(table)


@cli.command()
@click.argument("chart_name", type=click.Choice(CHART_NAMES, case_sensitive=False))
@click.option("--start", "start_date", default=None, help="Start date (YYYY-MM-DD)")
@click.option("--end", "end_date", default=None, help="End date (YYYY-MM-DD)")
@click.option(
    "--resolution", "-r",
    type=click.Choice(["day", "week", "month", "quarter", "year"]),
    default="month",
    help="Time resolution",
)
@click.option("--segment", "-s", default=None, help="Segment by dimension (e.g. country)")
@click.option("--json-output", "-j", is_flag=True, help="Output raw JSON")
def chart(chart_name, start_date, end_date, resolution, segment, json_output):
    """Fetch and display a chart's time-series data."""
    if not start_date or not end_date:
        start_date, end_date = _default_dates()

    with _get_client() as rc:
        data = rc.chart(
            chart_name,
            start_date=start_date,
            end_date=end_date,
            resolution=resolution,
            segment=segment,
        )

    if json_output:
        series = data.to_dict_series()
        click.echo(json.dumps(series, indent=2))
        return

    table = Table(title=f"{data.display_name} ({data.resolution})")
    table.add_column("Date", style="cyan")
    for m in data.measures:
        table.add_column(m.display_name, style="green", justify="right")

    # Group values by date
    from collections import defaultdict
    by_date: dict[str, dict[int, float]] = defaultdict(dict)
    for v in data.values:
        if not v.incomplete:
            by_date[v.date.isoformat()][v.measure_index] = v.value

    for d in sorted(by_date):
        row = [d]
        for i, m in enumerate(data.measures):
            val = by_date[d].get(i, 0)
            if m.unit == "$":
                row.append(f"${val:,.2f}")
            elif m.unit == "%":
                row.append(f"{val:.2f}%")
            else:
                row.append(f"{val:,.0f}")
        table.add_row(*row)

    console.print(table)

    # Summary
    if data.summary:
        console.print()
        for label, vals in data.summary.items():
            parts = [f"{k}: {v:,.2f}" for k, v in vals.items()]
            console.print(f"  [dim]{label.title()}:[/] {', '.join(parts)}")


@cli.command()
@click.option("--start", "start_date", default=None, help="Start date (YYYY-MM-DD)")
@click.option("--end", "end_date", default=None, help="End date (YYYY-MM-DD)")
@click.option("--resolution", "-r", default="month")
@click.option("--output", "-o", default="report.html", help="Output file path")
def report(start_date, end_date, resolution, output):
    """Generate a full subscription health report (HTML)."""
    if not start_date or not end_date:
        start_date, end_date = _default_dates()

    from rc_insights.report import generate_report

    with _get_client() as rc:
        console.print(f"[cyan]Fetching overview metrics...[/]")
        overview_data = rc.overview()

        console.print(f"[cyan]Fetching health charts...[/]")
        charts = rc.health_snapshot(
            start_date=start_date,
            end_date=end_date,
            resolution=resolution,
        )

    console.print(f"[cyan]Generating report...[/]")
    html = generate_report(overview_data, charts, start_date, end_date)

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)

    console.print(f"[green]Report saved to {output}[/]")


if __name__ == "__main__":
    cli()
