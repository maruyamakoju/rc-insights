# Video Tutorial Script: rc-insights in 2 Minutes

**Format:** Terminal screen recording with text overlay narration
**Duration:** ~2 minutes
**Tool:** asciinema recording → svg/gif conversion, or direct screen capture

---

## Scene 1: Introduction (0:00 - 0:15)

**Text overlay:** "rc-insights — RevenueCat Charts API, simplified"

```
# RevenueCat's Charts API has 21 chart types,
# segmentation, filtering, and 5 time resolutions.
#
# rc-insights wraps it all in a clean Python SDK + CLI.
# Let's see it in action.
```

## Scene 2: Installation (0:15 - 0:25)

```bash
$ pip install rc-insights
# ... Successfully installed rc-insights-0.1.0

$ export REVENUECAT_API_KEY=sk_...
$ export REVENUECAT_PROJECT_ID=proj...
```

**Text overlay:** "One pip install. Two env vars. That's the setup."

## Scene 3: Overview Command (0:25 - 0:45)

```bash
$ rc-insights overview
```

**Show the Rich table output:**
```
┌─────────────────────────────────────────────────────┐
│               RevenueCat Overview                    │
├────────────────────────┬──────────┬─────────────────┤
│ Metric                 │    Value │ Period           │
├────────────────────────┼──────────┼─────────────────┤
│ Active Trials          │       65 │ P0D              │
│ Active Subscriptions   │    2,529 │ P0D              │
│ MRR                    │$4,557.00 │ P28D             │
│ Revenue                │$5,105.00 │ P28D             │
│ New Customers          │    1,572 │ P28D             │
│ Active Users           │   13,957 │ P28D             │
└────────────────────────┴──────────┴─────────────────┘
```

**Text overlay:** "All your key metrics in one command."

## Scene 4: Chart Data (0:45 - 1:05)

```bash
$ rc-insights chart mrr --start 2025-01-01 --end 2025-12-31
```

**Show the table output with MRR by month**

```bash
# JSON output for piping to other tools
$ rc-insights chart mrr --start 2025-01-01 --end 2025-12-31 -j | jq '.values[-1]'
4411.46
```

**Text overlay:** "Query any of 21 chart types. Get JSON for automation."

## Scene 5: Python SDK (1:05 - 1:25)

```python
$ python
>>> from rc_insights import RCInsights
>>> rc = RCInsights(api_key="sk_...", project_id="proj...")
>>>
>>> overview = rc.overview()
>>> print(f"MRR: {overview['mrr'].formatted_value}")
MRR: $4,557.00
>>>
>>> mrr = rc.chart("mrr", start_date="2025-01-01", end_date="2025-12-31")
>>> for date, value in mrr.to_series()[-3:]:
...     print(f"  {date}: ${value:,.2f}")
  2025-10-01: $4,322.58
  2025-11-01: $4,421.66
  2025-12-01: $4,411.46
```

**Text overlay:** "Typed Python SDK. No JSON wrangling."

## Scene 6: Report Generation (1:25 - 1:50)

```bash
$ rc-insights report --start 2024-01-01 --end 2025-12-31 -o report.html
Fetching overview metrics...
Fetching health charts...
Generating report...
Report saved to report.html
```

**Cut to browser showing the HTML report:**
- Dark theme dashboard
- Metric cards at top (MRR, Active Subs, Trials, Revenue)
- Interactive Plotly charts
- Auto-generated insights section

**Text overlay:** "Beautiful reports. One command. Interactive charts."

## Scene 7: Closing (1:50 - 2:00)

```
# Install:
pip install rc-insights

# GitHub:
github.com/maruyamakoju/rc-insights

# Built by Claude (AI agent) for the RevenueCat developer community.
```

**Text overlay:** "Star the repo. Open an issue. Build something cool."

---

## Production Notes

- Record using asciinema (`asciinema rec demo.cast`) for terminal scenes
- Convert to SVG or GIF using `svg-term-cli` or `agg`
- Browser scenes: screenshot the actual report.html opened in Chrome
- Combine with a video editor or use `ffmpeg` to stitch scenes
- Alternative: Use Replit/CodeSandbox for a live-coding feel
- Add background music (royalty-free, lo-fi) at low volume
