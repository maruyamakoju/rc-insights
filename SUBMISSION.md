# RevenueCat Take-Home Assignment: Submission

**Candidate:** Mujin (@maruyamakoju)
**Agent:** Claude (Anthropic, Opus 4.6) operating via [agent-harness](https://github.com/maruyamakoju/agent-harness)
**Date:** March 17, 2026

---

## 1. Tool / Resource

**rc-insights** — Python SDK, CLI, and HTML report generator for RevenueCat Charts API v2.

- **GitHub Repository:** [github.com/maruyamakoju/rc-insights](https://github.com/maruyamakoju/rc-insights)
- **Live Report Demo:** [maruyamakoju.github.io/rc-insights](https://maruyamakoju.github.io/rc-insights/) — interactive HTML report generated from real Dark Noise data
- **PyPI:** `pip install rc-insights` ([pypi.org/project/rc-insights](https://pypi.org/project/rc-insights/))
- **Features:** Typed SDK for all 21 chart endpoints, CLI with Rich terminal output, interactive HTML report with Plotly charts and auto-generated insights
- **Tests:** 13 passing (pytest + respx mocking)
- **Real data:** Tested against Dark Noise via the provided API key

---

## 2. Long-Form Blog Post (1,800+ words)

**"Introducing rc-insights: The Missing Python SDK for RevenueCat's Charts API"**

- **Location:** [`docs/blog-post.md`](docs/blog-post.md)
- Includes code snippets, architecture diagram, real data analysis from Dark Noise, and CTA
- Publishing scripts included: [`scripts/publish_devto.py`](scripts/publish_devto.py), [`scripts/publish_hashnode.py`](scripts/publish_hashnode.py)

---

## 3. Video Tutorial (77 seconds)

**"rc-insights Demo"** — Terminal-style animated demo with typing animation, 1080p.

- **Video file:** [`assets/demo.mp4`](assets/demo.mp4)
- **Generation script:** [`scripts/make_video.py`](scripts/make_video.py) (Pillow + ffmpeg, fully reproducible)
- **11 scenes:** title card, problem statement, installation, overview command, MRR chart, JSON output, Python SDK, segmentation, report generation, report features, closing CTA
- Features typing animation with blinking cursor, color-coded output, fade transitions

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
├── scripts/               # Tooling
│   ├── make_video.py      # Video generator (Pillow + ffmpeg)
│   ├── publish_devto.py   # Dev.to blog publisher
│   └── publish_hashnode.py # Hashnode blog publisher
├── assets/
│   └── demo.mp4           # Demo video (77s, 1080p)
├── docs/                  # Content deliverables
│   ├── blog-post.md       # 1,800+ word launch blog post
│   ├── social-posts.md    # 5 Twitter/X posts
│   ├── growth-campaign.md # $100 growth campaign strategy
│   ├── video-script.md    # Video script & production notes
│   └── process-log.md     # Full process log
├── dist/                  # PyPI distribution files
├── report.html            # Sample report (Dark Noise real data)
├── pyproject.toml
├── README.md
└── SUBMISSION.md          # This file
```

---

*All deliverables were produced autonomously by Claude (Anthropic, Opus 4.6) running inside [agent-harness](https://github.com/maruyamakoju/agent-harness) — a 24/7 autonomous coding system. No human editing was applied to the content.*
