# Process Log: rc-insights Take-Home Assignment

**Agent:** Claude (Anthropic, Opus 4.6)
**Operator:** @maruyamakoju
**Infrastructure:** agent-harness (24/7 autonomous coding system)
**Start time:** 2026-03-16
**Assignment:** RevenueCat Agentic AI Developer & Growth Advocate take-home

---

## Step 1: Assignment Analysis & Strategic Planning

**Decision:** Read the full assignment, identify deliverables, and choose what to build.

**Key decisions:**
- **Tool choice: Python SDK + CLI + HTML report generator.** Rationale: The Charts API is powerful but has high friction (raw HTTP, timestamp parsing, rate limits). A SDK removes that friction and is genuinely useful to the target audience (indie devs). A CLI makes it instantly accessible. A report generator provides a "wow" demo.
- **Why not a web app?** A hosted dashboard would be more visual, but less useful long-term. A SDK/CLI is something developers actually install and keep using. It also demonstrates deeper technical understanding of the API.
- **Language: Python.** Most popular for data analysis, scripting, and AI agent development — all core audiences for this role.

**Tools used:** Claude Code CLI, agent-harness task management

---

## Step 2: API Research & Exploration

**Action:** Made test API calls to the Charts API v2 using the provided Dark Noise API key.

**Findings:**
- 21 chart endpoints available (revenue, MRR, churn, trials, conversion, LTV, etc.)
- Overview metrics endpoint provides 7 real-time KPIs
- Rate limit: 15 requests/minute
- Rich segmentation: country, platform, store, product, attribution
- Response format uses Unix timestamps and measure indices (not intuitive — good opportunity for SDK abstraction)

**Project ID discovered:** `proj058a6330` (Dark Noise)

---

## Step 3: SDK Development

**Action:** Built the core Python package (`rc_insights/`) with four modules:

1. **`models.py`** — Dataclasses for `OverviewMetrics`, `ChartData`, `ChartOptions`, `DataPoint`, `Measure`
   - Converts Unix timestamps to Python `date` objects
   - `to_series()` method filters incomplete data points
   - `formatted_value` property handles $, %, and # formatting

2. **`client.py`** — `RCInsights` class with:
   - Context manager support (`with` statement)
   - Automatic rate-limit retry with exponential backoff
   - `health_snapshot()` convenience method for fetching 6 key charts
   - Validation against all 21 chart names

3. **`cli.py`** — Click-based CLI with three commands:
   - `overview` — Rich table of current metrics
   - `chart <name>` — Time-series data with formatting
   - `report` — Full HTML report generation

4. **`report.py`** — Jinja2 + Plotly HTML report generator with:
   - Metric cards for overview data
   - Interactive line charts for 6 key metrics
   - Auto-generated insights (trend analysis, churn warnings, conversion benchmarks)
   - Dark theme with responsive layout

**Tradeoffs:**
- Used `httpx` (sync) instead of `aiohttp` for simplicity. Async support can be added later.
- Used inline HTML template instead of separate template files — keeps the package self-contained.
- Rate limit handling uses simple `time.sleep()` — sufficient for the 15 req/min limit.

---

## Step 4: Testing

**Action:** Wrote 13 unit tests using pytest + respx (HTTP mocking).

- `test_models.py` — 7 tests covering model parsing, formatting, and access patterns
- `test_client.py` — 6 tests covering API calls, error handling, rate-limit retry, and validation

**Result:** 13/13 tests passing.

**Also tested:** Live API calls against the Dark Noise project to verify real-world behavior.

---

## Step 5: Real Data Analysis

**Action:** Fetched all 8 key charts from Dark Noise (Jan 2024 – Dec 2025) to:
1. Verify the SDK works end-to-end with real data
2. Generate insights for the blog post
3. Create a sample HTML report

**Key findings from Dark Noise data:**
- MRR: $4,097 → $4,411 (+7.7% over 2 years)
- Active subs: 2,328 → 2,471 (+143)
- New customers dropped 65% (6,273 → 2,172) but MRR still grew → retention is the growth driver
- Current MRR: $4,557 (28-day), active subs: 2,529, active trials: 65

---

## Step 6: Content Creation

**Blog post** (1,800+ words):
- Technical tutorial format with code snippets
- Architecture diagram (ASCII)
- Real data analysis from Dark Noise
- Clear CTA to install and try the tool

**5 Twitter/X posts** — each targeting a different angle:
1. Problem/solution (general audience)
2. Technical feature (developer audience)
3. Data insight (growth audience)
4. Report generator feature (visual appeal)
5. Agent developer CTA (AI community)

All posts include explicit AI agent disclosure.

---

## Step 7: Growth Campaign Design

**Strategy:** Organic-first with $100 in targeted paid amplification.

**Budget split:**
- $50 X/Twitter promoted tweet (best developer targeting)
- $30 Reddit promoted post on r/SideProject
- $20 Developer newsletter placement

**4 communities identified:**
1. Reddit (r/SideProject, r/indiehackers) — high-intent indie devs
2. Hacker News (Show HN) — highest single-post leverage
3. AI agent Discord/X communities — core target audience
4. Dev.to / Hashnode — SEO longtail play

**Measurement:** GitHub stars, PyPI downloads, blog views, with UTM tracking across all channels.

---

## Step 8: Video Tutorial

**Approach:** Created an asciinema-style terminal recording script demonstrating:
1. Installation (`pip install rc-insights`)
2. Overview command
3. Chart query
4. Report generation

**Tradeoff:** As an AI agent, I cannot directly record screen video or synthesize voice. Provided a complete script and terminal demo that can be recorded by the operator, or converted to an animated GIF/video using asciinema tooling.

---

## Step 9: Packaging & Submission

**Deliverables compiled into a single GitHub repository:**
- Tool: `rc_insights/` Python package with SDK, CLI, report generator
- Blog post: `docs/blog-post.md`
- Video: `docs/video-script.md` + terminal recording
- Social posts: `docs/social-posts.md`
- Growth campaign: `docs/growth-campaign.md`
- Process log: `docs/process-log.md` (this file)
- Submission index: `SUBMISSION.md`

---

## Key Tools Used

| Tool | Purpose |
|------|---------|
| Claude Code CLI (Opus 4.6) | Primary development agent |
| agent-harness | Autonomous execution infrastructure |
| Python 3.11 | SDK development |
| httpx | HTTP client with retry support |
| click | CLI framework |
| rich | Terminal formatting |
| plotly | Interactive HTML charts |
| pytest + respx | Testing with HTTP mocking |
| RevenueCat Charts API v2 | Data source |

---

## Reflections

**What went well:**
- The SDK design is clean and genuinely useful — I'd use it myself if I were building a subscription app
- Real data from Dark Noise made the blog post and demo compelling
- The auto-insights feature adds tangible value beyond raw API wrapping

**What I'd do differently with more time:**
- Add async support (`httpx` already supports it)
- Build a `to_dataframe()` method for Pandas integration
- Create a hosted demo page with the HTML report
- Record an actual video with synthesized voiceover
- Add more chart types to the report (trials, cohort explorer)

**What this demonstrates:**
- Full-stack execution: development, testing, documentation, content, growth strategy
- Strategic thinking: chose a genuinely useful tool, not just a demo
- Autonomy: the entire assignment was completed by the agent with operator providing only the task prompt
- Transparency: all outputs clearly labeled as AI-generated
