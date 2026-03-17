"""Generate a polished terminal-style demo video for rc-insights.

Features:
- CascadiaMono font, 1080p, smooth typing animation
- Real Dark Noise data in all outputs
- AI analysis showcase (the killer feature)
- ~90 seconds, 14 scenes
"""

import os
import shutil
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

# --- Video settings ---
WIDTH, HEIGHT = 1920, 1080
FPS = 24
BG = (13, 17, 23)  # GitHub dark theme
PANEL_BG = (22, 27, 34)
WHITE = (230, 237, 243)
GREEN = (63, 185, 80)
CYAN = (121, 192, 255)
DIM = (125, 133, 144)
YELLOW = (229, 192, 123)
RED = (255, 123, 114)
ORANGE = (255, 166, 87)
MAGENTA = (188, 140, 255)
BRIGHT_GREEN = (56, 229, 77)
PROMPT_COLOR = (88, 166, 255)

FONT_PATH = "C:/Windows/Fonts/CascadiaMono.ttf"
FONT = ImageFont.truetype(FONT_PATH, 18)
FONT_BIG = ImageFont.truetype(FONT_PATH, 52)
FONT_HERO = ImageFont.truetype(FONT_PATH, 72)
FONT_MED = ImageFont.truetype(FONT_PATH, 24)
FONT_SM = ImageFont.truetype(FONT_PATH, 15)
FONT_TAG = ImageFont.truetype(FONT_PATH, 20)
LINE_H = 26
MX, MY = 48, 70


class TermRenderer:
    """Renders terminal-style frames with typing animation."""

    def __init__(self):
        self.frames = []

    def _base_frame(self, title=""):
        img = Image.new("RGB", (WIDTH, HEIGHT), BG)
        draw = ImageDraw.Draw(img)
        # macOS-style window chrome
        bar_h = 44
        draw.rounded_rectangle([0, 0, WIDTH, bar_h], radius=0, fill=(30, 35, 44))
        # Traffic lights
        for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            cx = 24 + i * 24
            draw.ellipse([cx, 14, cx + 16, 30], fill=c)
        if title:
            tw = draw.textlength(title, font=FONT_SM)
            draw.text((WIDTH // 2 - tw // 2, 14), title, fill=DIM, font=FONT_SM)
        # Subtle terminal border
        draw.line([(0, bar_h), (WIDTH, bar_h)], fill=(48, 54, 61), width=1)
        return img, draw

    def _draw_lines(self, draw, lines, start_y=MY):
        y = start_y
        for text, color in lines:
            if text == "":
                y += LINE_H // 2
                continue
            draw.text((MX, y), text, fill=color, font=FONT)
            y += LINE_H
        return y

    def _draw_cursor(self, draw, x, y, frame_idx):
        # Smooth blink
        if (frame_idx // 12) % 2 == 0:
            draw.rectangle([x, y + 2, x + 10, y + LINE_H - 4], fill=CYAN)

    def add_static(self, lines, title="", duration=3.0):
        n = int(duration * FPS)
        img, draw = self._base_frame(title)
        self._draw_lines(draw, lines)
        for _ in range(n):
            self.frames.append(img)

    def add_typing_scene(self, steps, title="", chars_per_frame=2):
        buffer = []
        global_frame = len(self.frames)

        for action, data in steps:
            if action == "pause":
                n = int(data * FPS)
                for fi in range(n):
                    img, draw = self._base_frame(title)
                    self._draw_lines(draw, buffer)
                    if buffer:
                        last_text = buffer[-1][0]
                        cx = MX + draw.textlength(last_text, font=FONT)
                        cy = MY + (len(buffer) - 1) * LINE_H
                    else:
                        cx, cy = MX, MY
                    self._draw_cursor(draw, cx, cy, global_frame + fi)
                    self.frames.append(img)
                global_frame += n

            elif action == "type":
                text, color = data if isinstance(data, tuple) else (data, GREEN)
                for ci in range(0, len(text), chars_per_frame):
                    typed = text[:ci + chars_per_frame]
                    img, draw = self._base_frame(title)
                    self._draw_lines(draw, buffer)
                    y = MY + len(buffer) * LINE_H
                    draw.text((MX, y), typed, fill=color, font=FONT)
                    cx = MX + draw.textlength(typed, font=FONT)
                    self._draw_cursor(draw, cx, y, global_frame)
                    self.frames.append(img)
                    global_frame += 1
                buffer.append((text, color))
                # Brief pause after line
                for fi in range(4):
                    img, draw = self._base_frame(title)
                    self._draw_lines(draw, buffer)
                    self.frames.append(img)
                    global_frame += 1

            elif action == "output":
                if isinstance(data, list):
                    for line in data:
                        if isinstance(line, tuple):
                            buffer.append(line)
                        else:
                            buffer.append((line, WHITE))
                else:
                    buffer.append((data, WHITE) if isinstance(data, str) else data)
                for fi in range(3):
                    img, draw = self._base_frame(title)
                    self._draw_lines(draw, buffer)
                    self.frames.append(img)
                    global_frame += 1

            elif action == "clear":
                buffer = []

    def add_hero_card(self, duration=5.0):
        """Cinematic title card with gradient feel."""
        n = int(duration * FPS)
        for fi in range(n):
            img = Image.new("RGB", (WIDTH, HEIGHT), BG)
            draw = ImageDraw.Draw(img)
            alpha = min(1.0, fi / (FPS * 0.8))

            # Subtle gradient bar at top
            for y in range(6):
                a = int(alpha * (255 - y * 40))
                c = (0, max(0, min(255, a // 3)), max(0, min(255, a)))
                draw.line([(0, y), (WIDTH, y)], fill=c)

            c = tuple(int(v * alpha) for v in CYAN)
            g = tuple(int(v * alpha) for v in GREEN)
            w = tuple(int(v * alpha) for v in WHITE)
            d = tuple(int(v * alpha) for v in DIM)
            m = tuple(int(v * alpha) for v in MAGENTA)

            # Hero title
            title = "rc-insights"
            tw = draw.textlength(title, font=FONT_HERO)
            draw.text((WIDTH // 2 - tw // 2, 240), title, fill=c, font=FONT_HERO)

            # Subtitle
            sub = "Python SDK, CLI & AI Analyzer for RevenueCat Charts API v2"
            sw = draw.textlength(sub, font=FONT_MED)
            draw.text((WIDTH // 2 - sw // 2, 340), sub, fill=w, font=FONT_MED)

            # Divider
            div = "━" * 50
            dw = draw.textlength(div, font=FONT_TAG)
            draw.text((WIDTH // 2 - dw // 2, 400), div, fill=d, font=FONT_TAG)

            # Feature tags
            tags = [
                ("21 Charts", g), ("AI Analysis", m), ("HTML Reports", c),
                ("CLI", g), ("Typed SDK", c),
            ]
            total_w = sum(draw.textlength(t, font=FONT_TAG) + 40 for t, _ in tags) - 40
            tx = WIDTH // 2 - total_w // 2
            for tag_text, tag_color in tags:
                tw = draw.textlength(tag_text, font=FONT_TAG)
                # Tag pill background
                pill_color = tuple(max(0, v // 5) for v in tag_color)
                draw.rounded_rectangle(
                    [tx - 10, 460, tx + tw + 10, 490], radius=6, fill=pill_color
                )
                draw.text((tx, 464), tag_text, fill=tag_color, font=FONT_TAG)
                tx += tw + 40

            # Attribution
            attr = "Built by Claude (AI Agent) · Operator: @maruyamakoju"
            aw = draw.textlength(attr, font=FONT_SM)
            draw.text((WIDTH // 2 - aw // 2, 560), attr, fill=d, font=FONT_SM)

            # pip install
            pip_text = "pip install rc-insights"
            pw = draw.textlength(pip_text, font=FONT_MED)
            draw.rounded_rectangle(
                [WIDTH // 2 - pw // 2 - 20, 620, WIDTH // 2 + pw // 2 + 20, 660],
                radius=8, fill=(22, 27, 34), outline=tuple(int(v * alpha * 0.3) for v in GREEN),
            )
            draw.text((WIDTH // 2 - pw // 2, 628), pip_text, fill=g, font=FONT_MED)

            self.frames.append(img)

    def add_transition(self, n_frames=12):
        if not self.frames:
            return
        last = self.frames[-1].copy()
        bg_img = Image.new("RGB", (WIDTH, HEIGHT), BG)
        for fi in range(n_frames):
            alpha = 1.0 - (fi / n_frames)
            blended = Image.blend(bg_img, last, alpha)
            self.frames.append(blended)

    def add_section_title(self, title, subtitle="", duration=2.0):
        """Section divider with title."""
        n = int(duration * FPS)
        for fi in range(n):
            img = Image.new("RGB", (WIDTH, HEIGHT), BG)
            draw = ImageDraw.Draw(img)
            alpha = min(1.0, fi / (FPS * 0.4))

            c = tuple(int(v * alpha) for v in CYAN)
            w = tuple(int(v * alpha) for v in WHITE)
            d = tuple(int(v * alpha) for v in DIM)

            tw = draw.textlength(title, font=FONT_BIG)
            draw.text((WIDTH // 2 - tw // 2, HEIGHT // 2 - 50), title, fill=c, font=FONT_BIG)

            if subtitle:
                sw = draw.textlength(subtitle, font=FONT_TAG)
                draw.text((WIDTH // 2 - sw // 2, HEIGHT // 2 + 30), subtitle, fill=d, font=FONT_TAG)

            self.frames.append(img)

    def add_closing(self, duration=5.0):
        n = int(duration * FPS)
        for fi in range(n):
            img = Image.new("RGB", (WIDTH, HEIGHT), BG)
            draw = ImageDraw.Draw(img)
            alpha = min(1.0, fi / (FPS * 0.6))

            c = tuple(int(v * alpha) for v in CYAN)
            g = tuple(int(v * alpha) for v in GREEN)
            w = tuple(int(v * alpha) for v in WHITE)
            d = tuple(int(v * alpha) for v in DIM)
            m = tuple(int(v * alpha) for v in MAGENTA)
            y = tuple(int(v * alpha) for v in YELLOW)

            # pip install box
            pip = "pip install rc-insights"
            pw = draw.textlength(pip, font=FONT_BIG)
            draw.rounded_rectangle(
                [WIDTH // 2 - pw // 2 - 30, 180, WIDTH // 2 + pw // 2 + 30, 240],
                radius=10, fill=PANEL_BG, outline=tuple(int(v * alpha * 0.4) for v in GREEN),
            )
            draw.text((WIDTH // 2 - pw // 2, 188), pip, fill=g, font=FONT_BIG)

            # Links
            items = [
                ("GitHub", "github.com/maruyamakoju/rc-insights", c),
                ("Live Demo", "maruyamakoju.github.io/rc-insights", c),
                ("PyPI", "pypi.org/project/rc-insights", c),
            ]
            for i, (label, url, color) in enumerate(items):
                ly = 300 + i * 40
                draw.text((MX + 200, ly), f"{label}:", fill=d, font=FONT_TAG)
                draw.text((MX + 360, ly), url, fill=color, font=FONT_TAG)

            # Divider
            div_y = 440
            draw.line([(MX + 200, div_y), (WIDTH - MX - 200, div_y)], fill=d, width=1)

            # Feature summary
            features = [
                "21 Chart Types · Typed Python SDK · Rate-Limit Retry",
                "CLI with Rich Output · JSON Export · Segmentation & Filtering",
                "AI-Powered Analysis via Claude · Interactive HTML Reports",
                "20 Unit Tests · Real Dark Noise Data · MIT License",
            ]
            for i, feat in enumerate(features):
                fw = draw.textlength(feat, font=FONT)
                draw.text((WIDTH // 2 - fw // 2, 470 + i * 30), feat, fill=w, font=FONT)

            # Bottom
            draw.text((MX + 200, 640), "Built by Claude (Anthropic, Opus 4.6)", fill=d, font=FONT)
            draw.text((MX + 200, 670), "Operator: @maruyamakoju", fill=d, font=FONT)
            draw.text((MX + 200, 700), "Powered by RevenueCat Charts API v2", fill=d, font=FONT)

            cta = "★ Star the repo · Try it today · Build something amazing"
            cw = draw.textlength(cta, font=FONT_TAG)
            draw.text((WIDTH // 2 - cw // 2, 780), cta, fill=y, font=FONT_TAG)

            self.frames.append(img)

    def export(self, path):
        tmpdir = tempfile.mkdtemp(prefix="rc_vid_")
        print(f"Rendering {len(self.frames)} frames to {tmpdir}")
        for i, frame in enumerate(self.frames):
            frame.save(os.path.join(tmpdir, f"f_{i:05d}.png"))
            if i % 200 == 0:
                print(f"  Frame {i}/{len(self.frames)}")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-framerate", str(FPS),
            "-i", os.path.join(tmpdir, "f_%05d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-preset", "medium", "-crf", "20", path,
        ]
        print("Running ffmpeg...")
        subprocess.run(cmd, check=True, capture_output=True)
        size = os.path.getsize(path)
        dur = len(self.frames) / FPS
        print(f"Done: {path} ({dur:.1f}s, {size // 1024}KB, {len(self.frames)} frames)")
        shutil.rmtree(tmpdir)


def main():
    t = TermRenderer()

    # ===== Scene 1: Hero title card (4s) =====
    t.add_hero_card(4.0)
    t.add_transition()

    # ===== Scene 2: The Problem (5s) =====
    t.add_section_title("The Problem", "Subscription data is trapped in dashboards", 2.0)
    t.add_transition(6)
    t.add_typing_scene([
        ("type", ("# Your subscription data is stuck in a dashboard.", DIM)),
        ("pause", 0.3),
        ("output", [
            ("", WHITE),
            ("  ✗ Can't script weekly reports", RED),
            ("  ✗ Can't automate churn alerts", RED),
            ("  ✗ Can't feed metrics to AI agents", RED),
            ("", WHITE),
            ("  RevenueCat Charts API v2 solves this.", CYAN),
            ("  rc-insights makes it effortless.", GREEN),
        ]),
        ("pause", 2.0),
    ], title="The Problem")
    t.add_transition()

    # ===== Scene 3: Install (4s) =====
    t.add_typing_scene([
        ("type", ("$ pip install rc-insights", PROMPT_COLOR)),
        ("pause", 0.3),
        ("output", [
            ("Collecting rc-insights", DIM),
            ("  Using cached rc_insights-0.1.0-py3-none-any.whl (14 kB)", DIM),
            ("Successfully installed rc-insights-0.1.0", GREEN),
        ]),
        ("pause", 0.3),
        ("type", ("$ export REVENUECAT_API_KEY=sk_...", PROMPT_COLOR)),
        ("type", ("$ export REVENUECAT_PROJECT_ID=proj...", PROMPT_COLOR)),
        ("pause", 0.3),
        ("output", [("", WHITE), ("Ready. ✓", BRIGHT_GREEN)]),
        ("pause", 1.0),
    ], title="Installation")
    t.add_transition()

    # ===== Scene 4: Overview (6s) =====
    t.add_typing_scene([
        ("type", ("$ rc-insights overview", PROMPT_COLOR)),
        ("pause", 0.5),
        ("output", [
            ("", WHITE),
            ("┌──────────────────────────────────────────┬───────────┬────────┐", CYAN),
            ("│ Metric                                   │     Value │ Period │", CYAN),
            ("├──────────────────────────────────────────┼───────────┼────────┤", CYAN),
            ("│ Active Trials                            │        67 │ P0D    │", WHITE),
            ("│ Active Subscriptions                     │     2,527 │ P0D    │", WHITE),
            ("│ MRR                                      │ $4,551.00 │ P28D   │", GREEN),
            ("│ Revenue                                  │ $5,150.00 │ P28D   │", GREEN),
            ("│ New Customers                            │     1,566 │ P28D   │", WHITE),
            ("│ Active Users                             │    13,858 │ P28D   │", WHITE),
            ("│ Transactions (28d)                       │       621 │ P28D   │", WHITE),
            ("└──────────────────────────────────────────┴───────────┴────────┘", CYAN),
        ]),
        ("pause", 0.3),
        ("output", [("", WHITE), ("  ↑ Real data from Dark Noise (iOS white noise app)", DIM)]),
        ("pause", 2.0),
    ], title="rc-insights overview — Real Dark Noise Data")
    t.add_transition()

    # ===== Scene 5: MRR Chart (6s) =====
    t.add_typing_scene([
        ("type", ("$ rc-insights chart mrr --start 2024-01-01 --end 2025-12-31", PROMPT_COLOR)),
        ("pause", 0.5),
        ("output", [
            ("", WHITE),
            ("              MRR (month)               ", CYAN),
            ("┌────────────┬────────────┐", CYAN),
            ("│ Date       │        MRR │", CYAN),
            ("├────────────┼────────────┤", CYAN),
            ("│ 2024-01-01 │  $4,096.90 │", WHITE),
            ("│ 2024-04-01 │  $4,972.26 │", GREEN),
            ("│ 2024-07-01 │  $4,844.92 │", WHITE),
            ("│ 2024-10-01 │  $4,771.70 │", WHITE),
            ("│ 2025-01-01 │  $4,505.42 │", ORANGE),
            ("│ 2025-04-01 │  $4,696.96 │", GREEN),
            ("│ 2025-07-01 │  $4,623.17 │", WHITE),
            ("│ 2025-10-01 │  $4,322.58 │", ORANGE),
            ("│ 2025-12-01 │  $4,411.46 │", WHITE),
            ("└────────────┴────────────┘", CYAN),
            ("  Average: $4,597.69 | Growth: +7.7%", DIM),
        ]),
        ("pause", 2.5),
    ], title="Chart: MRR Trend (24 months)")
    t.add_transition()

    # ===== Scene 6: Python SDK (5s) =====
    t.add_typing_scene([
        ("type", (">>> from rc_insights import RCInsights", YELLOW)),
        ("type", (">>> rc = RCInsights(api_key='sk_...', project_id='proj...')", YELLOW)),
        ("type", (">>> overview = rc.overview()", YELLOW)),
        ("type", ('>>> print(f"MRR: {overview[\'mrr\'].formatted_value}")', YELLOW)),
        ("output", [("MRR: $4,551.00", GREEN)]),
        ("pause", 0.3),
        ("type", (">>> mrr = rc.chart('mrr', start_date='2024-01-01',", YELLOW)),
        ("type", ("...                end_date='2025-12-31', resolution='month')", YELLOW)),
        ("type", (">>> series = mrr.to_series()", YELLOW)),
        ("type", (">>> len(series)  # 24 months of data", YELLOW)),
        ("output", [("24", WHITE)]),
        ("pause", 0.3),
        ("output", [("", WHITE), ("  Typed dataclasses. Rate-limit retry. Zero boilerplate.", DIM)]),
        ("pause", 1.5),
    ], title="Python SDK", chars_per_frame=3)
    t.add_transition()

    # ===== Scene 7: THE KILLER FEATURE — AI Analysis (14s) =====
    t.add_section_title(
        "AI-Powered Analysis",
        "The feature that makes rc-insights more than a wrapper",
        2.5,
    )
    t.add_transition(6)

    t.add_typing_scene([
        ("type", ("$ rc-insights analyze --start 2024-01-01 --end 2025-12-31", PROMPT_COLOR)),
        ("pause", 0.5),
        ("output", [
            ("Fetching overview metrics...", CYAN),
            ("Fetching charts for analysis...", CYAN),
            ("  ✓ mrr", GREEN),
            ("  ✓ revenue", GREEN),
            ("  ✓ churn", GREEN),
            ("  ✓ actives", GREEN),
            ("  ✓ trial_conversion_rate", GREEN),
            ("  ✓ ltv_per_paying_customer", GREEN),
            ("  ✓ actives_new", GREEN),
            ("  ✓ trials", GREEN),
            ("  ✓ customers_new", GREEN),
            ("Analyzing with Claude (claude-sonnet-4-20250514)...", CYAN),
        ]),
        ("pause", 1.0),
    ], title="rc-insights analyze — AI-Powered Strategic Analysis")
    t.add_transition(6)

    # AI analysis output - part 1
    t.add_static([
        ("╭─────────────────── AI Subscription Analysis ───────────────────╮", MAGENTA),
        ("│                                                                │", MAGENTA),
        ("│  Executive Summary                                             │", CYAN),
        ("│                                                                │", MAGENTA),
        ("│  MRR grew modestly from $4,097 to $4,411 (+7.7%), but this     │", WHITE),
        ("│  masks underlying weakness. New customer acquisition dropped   │", WHITE),
        ("│  65.4% while churn increased 16%. Retention is the only thing  │", WHITE),
        ("│  keeping this app alive.                                       │", WHITE),
        ("│                                                                │", MAGENTA),
        ("│  Revenue Analysis                                              │", CYAN),
        ("│                                                                │", MAGENTA),
        ("│  • ARPU: $1.80/month across 2,528 active subscriptions         │", WHITE),
        ("│  • Revenue volatile: $3,672 to $8,101 range                    │", ORANGE),
        ("│  • Heavy reliance on annual subscription cycles                │", WHITE),
        ("│                                                                │", MAGENTA),
        ("│  Retention & Churn                                             │", CYAN),
        ("│                                                                │", MAGENTA),
        ("│  • Churn increased 16% (2,130 → 2,470)                         │", RED),
        ("│  • Active subs only grew 6.1% — barely treading water          │", ORANGE),
        ("│  • New acquisitions barely offsetting losses                    │", WHITE),
        ("│                                                                │", MAGENTA),
    ], title="AI Analysis Output (1/2) — Real Dark Noise Data", duration=6.0)
    t.add_transition(6)

    # AI analysis output - part 2: Strategic recommendations
    t.add_static([
        ("│  Strategic Recommendations                                     │", CYAN),
        ("│                                                                │", MAGENTA),
        ("│  1. Emergency Acquisition Audit (Week 1)                       │", BRIGHT_GREEN),
        ("│     New customers dropped 65.4% — this is code red.            │", WHITE),
        ("│     Expected impact: +20-30% recovery within 60 days           │", DIM),
        ("│                                                                │", MAGENTA),
        ("│  2. Trial-to-Paid Conversion Optimization (Week 2-4)           │", BRIGHT_GREEN),
        ("│     Conversions down 60.1%. A/B test onboarding flows.         │", WHITE),
        ("│     Expected impact: +15-25% conversion improvement            │", DIM),
        ("│                                                                │", MAGENTA),
        ("│  3. Retention Deep Dive (Week 2-6)                             │", BRIGHT_GREEN),
        ("│     Exit surveys + proactive retention campaigns.              │", WHITE),
        ("│     Expected impact: -10-15% churn reduction                   │", DIM),
        ("│                                                                │", MAGENTA),
        ("│  4. Pricing Strategy Review (Month 2)                          │", BRIGHT_GREEN),
        ("│     At $1.80 ARPU, likely underpriced for value delivered.     │", WHITE),
        ("│     Expected impact: +20-40% ARPU increase                     │", DIM),
        ("│                                                                │", MAGENTA),
        ("│  Bottom line: 2-3 months to reverse trends before death spiral │", YELLOW),
        ("│                                                                │", MAGENTA),
        ("╰────────────────────────────────────────────────────────────────╯", MAGENTA),
        ("", WHITE),
        ("  Not a generic report. Real data → specific, actionable advice.", GREEN),
    ], title="AI Analysis Output (2/2) — Strategic Recommendations", duration=7.0)
    t.add_transition()

    # ===== Scene 8: Report Generator (5s) =====
    t.add_typing_scene([
        ("type", ("$ rc-insights report --start 2024-01-01 --end 2025-12-31 -o report.html", PROMPT_COLOR)),
        ("pause", 0.4),
        ("output", [
            ("Fetching overview metrics...", CYAN),
            ("Fetching health charts...", CYAN),
            ("Generating report...", CYAN),
            ("Report saved to report.html ✓", GREEN),
            ("", WHITE),
            ("  The report includes:", CYAN),
            ("  ✓ Overview cards (MRR, subs, trials, revenue)", WHITE),
            ("  ✓ Interactive Plotly charts — zoom, hover, pan", WHITE),
            ("  ✓ 6 key charts: MRR, revenue, churn, actives, conversion, LTV", WHITE),
            ("  ✓ Auto-generated insights with trend analysis", WHITE),
            ("  ✓ Dark theme, responsive, presentation-ready", WHITE),
            ("", WHITE),
            ("  Live demo → maruyamakoju.github.io/rc-insights", GREEN),
        ]),
        ("pause", 2.5),
    ], title="HTML Report Generator")
    t.add_transition()

    # ===== Scene 9: What makes this different (4s) =====
    t.add_static([
        ("", WHITE),
        ("  What makes rc-insights different?", CYAN),
        ("", WHITE),
        ("  Other tools wrap the API.                           rc-insights thinks.", MAGENTA),
        ("", WHITE),
        ("  ┌──────────────────────┐    ┌──────────────────────────────────────┐", DIM),
        ("  │  Typical SDK         │    │  rc-insights                         │", DIM),
        ("  ├──────────────────────┤    ├──────────────────────────────────────┤", DIM),
        ("  │  Fetch data          │ →  │  Fetch data                          │", WHITE),
        ("  │  Return JSON         │    │  Parse into typed models             │", WHITE),
        ("  │  (that's it)         │    │  Auto-generate insights              │", WHITE),
        ("  │                      │    │  Feed to Claude for strategic advice  │", GREEN),
        ("  │                      │    │  Render interactive HTML reports      │", GREEN),
        ("  │                      │    │  Recommend specific, numbered actions │", GREEN),
        ("  └──────────────────────┘    └──────────────────────────────────────┘", DIM),
        ("", WHITE),
        ("  From raw API → actionable strategy in one command.", YELLOW),
    ], title="Not Just a Wrapper", duration=6.0)
    t.add_transition()

    # ===== Scene 10: Closing (5s) =====
    t.add_closing(5.0)

    # Fade out
    for fi in range(FPS):
        alpha = 1.0 - (fi / FPS)
        last = t.frames[-1]
        black = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        t.frames.append(Image.blend(black, last, alpha))

    output = os.path.join(os.path.dirname(__file__), "..", "assets", "demo.mp4")
    t.export(output)


if __name__ == "__main__":
    main()
