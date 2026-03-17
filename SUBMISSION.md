# RevenueCat Take-Home Assignment: Submission

**Candidate:** Mujin (@maruyamakoju)
**Agent:** Claude (Anthropic, Opus 4.6) operating via [agent-harness](https://github.com/maruyamakoju/agent-harness)
**Date:** March 16, 2026

---

## 1. Tool / Resource

**rc-insights** — Python SDK, CLI, and HTML report generator for RevenueCat Charts API v2.

- **GitHub Repository:** [github.com/maruyamakoju/rc-insights](https://github.com/maruyamakoju/rc-insights)
- **Features:** Typed SDK for all 21 chart endpoints, CLI with Rich terminal output, interactive HTML report with Plotly charts and auto-generated insights
- **Tests:** 13 passing (pytest + respx mocking)
- **Real data:** Tested against Dark Noise via the provided API key

---

## 2. Long-Form Blog Post (1,800+ words)

**"Introducing rc-insights: The Missing Python SDK for RevenueCat's Charts API"**

- **Location:** [`docs/blog-post.md`](docs/blog-post.md)
- Includes code snippets, architecture diagram, real data analysis from Dark Noise, and CTA
- Ready for cross-posting to Dev.to / Hashnode

---

## 3. Video Tutorial

**"rc-insights in 25 Seconds"** — Terminal-style animated demo video.

- **Video file:** [`assets/demo.mp4`](assets/demo.mp4)
- **Script:** [`docs/video-script.md`](docs/video-script.md)
- **Generation script:** [`scripts/make_video.py`](scripts/make_video.py) (Pillow + ffmpeg)
- Covers: installation, overview command, chart queries, Python SDK, report generation
- 7 scenes demonstrating all key features with terminal-style rendering

---

## 4. Social Media Posts (5 posts for X/Twitter)

- **Location:** [`docs/social-posts.md`](docs/social-posts.md)
- Post 1: Problem/solution (general audience)
- Post 2: Technical feature deep-dive (developers)
- Post 3: Surprising data insight from Dark Noise (growth audience)
- Post 4: Report generator feature showcase (visual appeal)
- Post 5: Call to action for AI agent developers
- All posts include explicit AI agent disclosure

---

## 5. Growth Campaign Report

- **Location:** [`docs/growth-campaign.md`](docs/growth-campaign.md)
- **$100 budget allocation:** $50 X/Twitter promoted tweet, $30 Reddit promoted post, $20 developer newsletter
- **4 communities targeted:** Reddit (r/SideProject, r/indiehackers), Hacker News, AI agent Discord/X, Dev.to/Hashnode
- **Measurement plan:** GitHub stars, PyPI downloads, blog views with UTM tracking
- **2-week timeline** with day-by-day posting schedule

---

## 6. Process Log

- **Location:** [`docs/process-log.md`](docs/process-log.md)
- 9-step workflow from assignment analysis through final packaging
- Key decisions, tradeoffs, tools used, and reflections
- Demonstrates autonomous execution across development, content, and strategy

---

## Repository Structure

```
rc-insights/
├── rc_insights/           # Python SDK
│   ├── __init__.py
│   ├── client.py          # API client (auth, retry, all 21 charts)
│   ├── models.py          # Typed dataclasses for API responses
│   ├── cli.py             # Click CLI (overview, chart, report)
│   └── report.py          # HTML report generator (Plotly + insights)
├── tests/                 # 13 unit tests
│   ├── test_models.py
│   └── test_client.py
├── examples/              # Usage examples
│   ├── quick_start.py
│   ├── generate_report.py
│   └── segmented_analysis.py
├── docs/                  # Content deliverables
│   ├── blog-post.md
│   ├── social-posts.md
│   ├── growth-campaign.md
│   ├── video-script.md
│   └── process-log.md
├── report.html            # Sample report (generated from Dark Noise data)
├── pyproject.toml
├── README.md
└── SUBMISSION.md          # This file
```

---

*All deliverables were produced autonomously by Claude (Anthropic) running inside agent-harness. No human editing was applied to the content.*
