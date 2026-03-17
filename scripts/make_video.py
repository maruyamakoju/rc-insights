"""Generate a terminal-style demo video with typing animation for rc-insights."""

import os
import shutil
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont

# --- Video settings ---
WIDTH, HEIGHT = 1920, 1080
FPS = 15
BG = (15, 15, 35)
WHITE = (224, 224, 224)
GREEN = (29, 185, 84)
CYAN = (0, 212, 255)
DIM = (100, 100, 120)
YELLOW = (255, 214, 10)
RED = (255, 95, 86)
ORANGE = (255, 160, 50)

FONT_PATH = "C:/Windows/Fonts/consola.ttf"
FONT = ImageFont.truetype(FONT_PATH, 20)
FONT_BIG = ImageFont.truetype(FONT_PATH, 44)
FONT_MED = ImageFont.truetype(FONT_PATH, 26)
FONT_SM = ImageFont.truetype(FONT_PATH, 16)
LINE_H = 28
MX, MY = 40, 80  # margins


class TermRenderer:
    """Renders terminal-style frames with typing animation."""

    def __init__(self):
        self.frames = []

    def _base_frame(self, title=""):
        img = Image.new("RGB", (WIDTH, HEIGHT), BG)
        draw = ImageDraw.Draw(img)
        # Window chrome
        draw.rounded_rectangle([16, 12, WIDTH - 16, 52], radius=10, fill=(30, 30, 60))
        for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            draw.ellipse([32 + i * 26, 22, 48 + i * 26, 38], fill=c)
        if title:
            draw.text((WIDTH // 2 - len(title) * 5, 22), title, fill=DIM, font=FONT_SM)
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
        if (frame_idx // 7) % 2 == 0:
            draw.rectangle([x, y, x + 12, y + LINE_H - 4], fill=GREEN)

    def add_static(self, lines, title="", duration=3.0):
        """Add a static scene."""
        n = int(duration * FPS)
        img, draw = self._base_frame(title)
        self._draw_lines(draw, lines)
        for _ in range(n):
            self.frames.append(img)

    def add_typing_scene(self, steps, title="", chars_per_frame=2):
        """steps: list of (action, data) where action is 'type', 'output', 'pause', 'clear'."""
        buffer = []  # list of (text, color) tuples
        cursor_line = 0
        global_frame = len(self.frames)

        for action, data in steps:
            if action == "pause":
                n = int(data * FPS)
                for fi in range(n):
                    img, draw = self._base_frame(title)
                    self._draw_lines(draw, buffer)
                    y = MY + len(buffer) * LINE_H
                    # cursor at end of last line
                    if buffer:
                        last_text = buffer[-1][0]
                        cx = MX + len(last_text) * 10
                        cy = MY + (len(buffer) - 1) * LINE_H
                    else:
                        cx, cy = MX, MY
                    self._draw_cursor(draw, cx, cy, global_frame + fi)
                    self.frames.append(img)
                global_frame += n

            elif action == "type":
                text, color = data if isinstance(data, tuple) else (data, GREEN)
                typed = ""
                for ci in range(0, len(text), chars_per_frame):
                    typed = text[:ci + chars_per_frame]
                    img, draw = self._base_frame(title)
                    self._draw_lines(draw, buffer)
                    y = MY + len(buffer) * LINE_H
                    draw.text((MX, y), typed, fill=color, font=FONT)
                    cx = MX + len(typed) * 10
                    self._draw_cursor(draw, cx, y, global_frame)
                    self.frames.append(img)
                    global_frame += 1
                buffer.append((text, color))
                # brief pause after typing
                for fi in range(3):
                    img, draw = self._base_frame(title)
                    self._draw_lines(draw, buffer)
                    self.frames.append(img)
                    global_frame += 1

            elif action == "output":
                # instant output lines
                if isinstance(data, list):
                    for line in data:
                        if isinstance(line, tuple):
                            buffer.append(line)
                        else:
                            buffer.append((line, WHITE))
                else:
                    buffer.append((data, WHITE) if isinstance(data, str) else data)
                # render 2 frames for the output appearing
                for fi in range(2):
                    img, draw = self._base_frame(title)
                    self._draw_lines(draw, buffer)
                    self.frames.append(img)
                    global_frame += 1

            elif action == "clear":
                buffer = []

    def add_title_card(self, duration=5.0):
        n = int(duration * FPS)
        for fi in range(n):
            img = Image.new("RGB", (WIDTH, HEIGHT), BG)
            draw = ImageDraw.Draw(img)
            # fade in
            alpha = min(1.0, fi / (FPS * 1.0))
            c = tuple(int(v * alpha) for v in CYAN)
            g = tuple(int(v * alpha) for v in GREEN)
            w = tuple(int(v * alpha) for v in WHITE)
            d = tuple(int(v * alpha) for v in DIM)

            draw.text((WIDTH // 2 - 260, 280), "rc-insights", fill=c, font=FONT_BIG)
            draw.text((WIDTH // 2 - 380, 360), "Python SDK + CLI for RevenueCat Charts API v2", fill=w, font=FONT_MED)
            draw.text((WIDTH // 2 - 260, 420), "────────────────────────────────", fill=d, font=FONT)
            draw.text((WIDTH // 2 - 300, 480), "21 chart types · Segmentation · HTML Reports", fill=g, font=FONT)
            draw.text((WIDTH // 2 - 310, 530), "Built by Claude (AI Agent) for @maruyamakoju", fill=d, font=FONT)
            self.frames.append(img)

    def add_transition(self, n_frames=8):
        """Fade to black transition."""
        if not self.frames:
            return
        last = self.frames[-1].copy()
        for fi in range(n_frames):
            alpha = 1.0 - (fi / n_frames)
            overlay = Image.new("RGB", (WIDTH, HEIGHT), BG)
            blended = Image.blend(overlay, last, alpha)
            self.frames.append(blended)

    def add_closing(self, duration=5.0):
        n = int(duration * FPS)
        for fi in range(n):
            img = Image.new("RGB", (WIDTH, HEIGHT), BG)
            draw = ImageDraw.Draw(img)
            alpha = min(1.0, fi / (FPS * 0.8))
            g = tuple(int(v * alpha) for v in GREEN)
            c = tuple(int(v * alpha) for v in CYAN)
            w = tuple(int(v * alpha) for v in WHITE)
            d = tuple(int(v * alpha) for v in DIM)
            y = tuple(int(v * alpha) for v in YELLOW)

            draw.text((MX + 200, 200), "pip install rc-insights", fill=g, font=FONT_MED)
            draw.text((MX + 200, 280), "github.com/maruyamakoju/rc-insights", fill=c, font=FONT)
            draw.text((MX + 200, 340), "21 chart types · Segmentation · Filtering", fill=w, font=FONT)
            draw.text((MX + 200, 380), "CLI · Python SDK · HTML Reports · 13 Tests", fill=w, font=FONT)
            draw.text((MX + 200, 450), "─────────────────────────────────────────", fill=d, font=FONT)
            draw.text((MX + 200, 490), "Built by Claude (AI Agent, Anthropic)", fill=d, font=FONT)
            draw.text((MX + 200, 530), "Operator: @maruyamakoju", fill=d, font=FONT)
            draw.text((MX + 200, 570), "Powered by RevenueCat Charts API v2", fill=d, font=FONT)
            draw.text((MX + 200, 640), "★ Star the repo. Open an issue. Build something cool.", fill=y, font=FONT)
            self.frames.append(img)

    def export(self, path):
        tmpdir = tempfile.mkdtemp(prefix="rc_vid_")
        print(f"Rendering {len(self.frames)} frames to {tmpdir}")
        for i, frame in enumerate(self.frames):
            frame.save(os.path.join(tmpdir, f"f_{i:05d}.png"))
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-framerate", str(FPS),
            "-i", os.path.join(tmpdir, "f_%05d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-preset", "medium", "-crf", "22", path,
        ]
        print("Running ffmpeg...")
        subprocess.run(cmd, check=True, capture_output=True)
        size = os.path.getsize(path)
        dur = len(self.frames) / FPS
        print(f"Video: {path} ({dur:.1f}s, {size // 1024}KB, {len(self.frames)} frames)")
        shutil.rmtree(tmpdir)


def main():
    t = TermRenderer()

    # --- Scene 1: Title card (5s) ---
    t.add_title_card(5.0)
    t.add_transition()

    # --- Scene 2: The Problem (7s) ---
    t.add_typing_scene([
        ("type", ("# The Problem", CYAN)),
        ("pause", 0.5),
        ("output", [
            ("", WHITE),
            ("Your subscription data is trapped in a dashboard.", WHITE),
            ("You can't script it. You can't automate it.", WHITE),
            ("You can't feed it to an AI agent.", WHITE),
            ("", WHITE),
            ("RevenueCat's Charts API v2 changes that.", GREEN),
            ("21 chart endpoints. Segmentation. Filtering.", GREEN),
            ("", WHITE),
            ("But raw HTTP calls are tedious...", DIM),
            ("rc-insights makes it simple.", CYAN),
        ]),
        ("pause", 2.5),
    ], title="The Problem")
    t.add_transition()

    # --- Scene 3: Installation (7s) ---
    t.add_typing_scene([
        ("type", ("$ pip install rc-insights", GREEN)),
        ("pause", 0.3),
        ("output", [
            ("Collecting rc-insights", DIM),
            ("  Downloading rc_insights-0.1.0-py3-none-any.whl (12 kB)", DIM),
            ("Installing collected packages: httpx, click, rich, plotly, rc-insights", DIM),
            ("Successfully installed rc-insights-0.1.0", GREEN),
        ]),
        ("pause", 0.8),
        ("type", ("$ export REVENUECAT_API_KEY=sk_...", GREEN)),
        ("type", ("$ export REVENUECAT_PROJECT_ID=proj...", GREEN)),
        ("pause", 0.5),
        ("output", [("", WHITE), ("✓ One pip install. Two env vars. Ready to go.", GREEN)]),
        ("pause", 1.5),
    ], title="Installation")
    t.add_transition()

    # --- Scene 4: Overview command (10s) ---
    t.add_typing_scene([
        ("type", ("$ rc-insights overview", GREEN)),
        ("pause", 0.5),
        ("output", [
            ("", WHITE),
            ("┌──────────────────────────────────────────────────────┐", CYAN),
            ("│              RevenueCat Overview                     │", CYAN),
            ("├────────────────────────┬───────────┬─────────────────┤", CYAN),
            ("│ Metric                 │     Value │ Period          │", CYAN),
            ("├────────────────────────┼───────────┼─────────────────┤", CYAN),
        ]),
        ("pause", 0.3),
        ("output", [
            ("│ Active Trials          │        65 │ P0D             │", WHITE),
            ("│ Active Subscriptions   │     2,529 │ P0D             │", WHITE),
            ("│ MRR                    │ $4,557.00 │ P28D            │", GREEN),
            ("│ Revenue                │ $5,105.00 │ P28D            │", GREEN),
            ("│ New Customers          │     1,572 │ P28D            │", WHITE),
            ("│ Active Users           │    13,957 │ P28D            │", WHITE),
            ("│ Transactions (28d)     │       616 │ P28D            │", WHITE),
            ("└────────────────────────┴───────────┴─────────────────┘", CYAN),
        ]),
        ("pause", 0.5),
        ("output", [("", WHITE), ("  Real data from Dark Noise — all metrics, one command.", DIM)]),
        ("pause", 2.0),
    ], title="rc-insights overview")
    t.add_transition()

    # --- Scene 5: MRR Chart (10s) ---
    t.add_typing_scene([
        ("type", ("$ rc-insights chart mrr --start 2025-01-01 --end 2025-12-31", GREEN)),
        ("pause", 0.5),
        ("output", [
            ("", WHITE),
            ("                  MRR (month)                          ", CYAN),
            ("┌────────────┬────────────┐", CYAN),
            ("│ Date       │        MRR │", CYAN),
            ("├────────────┼────────────┤", CYAN),
        ]),
        ("pause", 0.2),
        ("output", [
            ("│ 2025-01-01 │  $4,505.42 │", WHITE),
            ("│ 2025-02-01 │  $4,583.13 │", WHITE),
            ("│ 2025-03-01 │  $4,636.80 │", GREEN),
            ("│ 2025-04-01 │  $4,696.96 │", GREEN),
            ("│ 2025-05-01 │  $4,669.40 │", WHITE),
            ("│ 2025-06-01 │  $4,559.29 │", ORANGE),
            ("│ 2025-07-01 │  $4,623.17 │", WHITE),
            ("│ 2025-08-01 │  $4,587.34 │", WHITE),
            ("│ 2025-09-01 │  $4,460.63 │", ORANGE),
            ("│ 2025-10-01 │  $4,322.58 │", ORANGE),
            ("│ 2025-11-01 │  $4,421.66 │", GREEN),
            ("│ 2025-12-01 │  $4,411.46 │", WHITE),
            ("└────────────┴────────────┘", CYAN),
        ]),
        ("pause", 0.5),
        ("output", [
            ("  Average: $4,539.68  Total: $54,476.22", DIM),
        ]),
        ("pause", 2.0),
    ], title="Chart: MRR")
    t.add_transition()

    # --- Scene 6: JSON output (6s) ---
    t.add_typing_scene([
        ("type", ("$ rc-insights chart mrr -j | jq '.values[-3:]'", GREEN)),
        ("pause", 0.4),
        ("output", [
            ("", WHITE),
            ("[", YELLOW),
            ('  4322.58,', YELLOW),
            ('  4421.66,', YELLOW),
            ('  4411.46', YELLOW),
            ("]", YELLOW),
        ]),
        ("pause", 0.5),
        ("output", [
            ("", WHITE),
            ("  Pipe to jq, pandas, or feed to an AI agent.", DIM),
        ]),
        ("pause", 2.0),
    ], title="JSON Output")
    t.add_transition()

    # --- Scene 7: Python SDK (12s) ---
    t.add_typing_scene([
        ("type", (">>> from rc_insights import RCInsights", YELLOW)),
        ("type", (">>> rc = RCInsights(api_key='sk_...', project_id='proj...')", YELLOW)),
        ("pause", 0.3),
        ("type", (">>> overview = rc.overview()", YELLOW)),
        ("type", ('>>> print(f"MRR: {overview[\'mrr\'].formatted_value}")', YELLOW)),
        ("output", [("MRR: $4,557.00", GREEN)]),
        ("pause", 0.5),
        ("type", (">>> mrr = rc.chart('mrr', start_date='2025-01-01',", YELLOW)),
        ("type", ("...                end_date='2025-12-31', resolution='month')", YELLOW)),
        ("type", (">>> for date, value in mrr.to_series()[-3:]:", YELLOW)),
        ("type", ("...     print(f'  {date}: ${value:,.2f}')", YELLOW)),
        ("output", [
            ("  2025-10-01: $4,322.58", WHITE),
            ("  2025-11-01: $4,421.66", WHITE),
            ("  2025-12-01: $4,411.46", WHITE),
        ]),
        ("pause", 0.5),
        ("output", [("", WHITE), ("  Typed dataclasses. No JSON wrangling needed.", DIM)]),
        ("pause", 2.0),
    ], title="Python SDK", chars_per_frame=3)
    t.add_transition()

    # --- Scene 8: Segmentation (8s) ---
    t.add_typing_scene([
        ("type", (">>> revenue = rc.chart('revenue', segment='country',", YELLOW)),
        ("type", ("...     start_date='2025-01-01', end_date='2025-12-31')", YELLOW)),
        ("pause", 0.3),
        ("output", [
            ("", WHITE),
            ("# Segmentation by country, platform, store, product...", DIM),
            ("# Filter to specific stores:", DIM),
        ]),
        ("type", (">>> mrr_ios = rc.chart('mrr', filters={'store': 'app_store'})", YELLOW)),
        ("pause", 0.3),
        ("output", [
            ("", WHITE),
            ("  21 charts × unlimited segments × flexible filters", GREEN),
            ("  Programmatic access to your full analytics stack.", DIM),
        ]),
        ("pause", 2.0),
    ], title="Segmentation & Filtering")
    t.add_transition()

    # --- Scene 9: Report (10s) ---
    t.add_typing_scene([
        ("type", ("$ rc-insights report --start 2024-01-01 --end 2025-12-31 -o report.html", GREEN)),
        ("pause", 0.4),
        ("output", [
            ("Fetching overview metrics...", CYAN),
            ("Fetching health charts...", CYAN),
        ]),
        ("pause", 0.3),
        ("output", [
            ("  ✓ mrr: 24 data points", GREEN),
            ("  ✓ revenue: 24 data points", GREEN),
            ("  ✓ churn: 24 data points", GREEN),
            ("  ✓ actives: 24 data points", GREEN),
            ("  ✓ trial_conversion_rate: 23 data points", GREEN),
            ("  ✓ ltv_per_paying_customer: 24 data points", GREEN),
        ]),
        ("pause", 0.3),
        ("output", [
            ("Generating report...", CYAN),
            ("Report saved to report.html", GREEN),
            ("", WHITE),
            ("Key Insights:", CYAN),
            ("  • MRR grew 7.7% ($4,097 → $4,411)", WHITE),
            ("  • Active subscriptions +143 over the period", WHITE),
            ("  • LTV per paying customer: $146.00", WHITE),
            ("  • Retention is the primary growth driver", GREEN),
        ]),
        ("pause", 2.5),
    ], title="Report Generator")
    t.add_transition()

    # --- Scene 10: Report features (6s) ---
    t.add_static([
        ("", WHITE),
        ("  The HTML report includes:", CYAN),
        ("", WHITE),
        ("  ✓  Overview metric cards (MRR, subs, trials, revenue)", WHITE),
        ("  ✓  Interactive Plotly charts — zoom, hover, pan", WHITE),
        ("  ✓  6 key charts: MRR, revenue, churn, actives, conversion, LTV", WHITE),
        ("  ✓  Auto-generated insights with trend analysis", WHITE),
        ("  ✓  Churn warnings and conversion benchmarks", WHITE),
        ("  ✓  Dark theme, responsive, presentation-ready", WHITE),
        ("", WHITE),
        ("  Live demo: maruyamakoju.github.io/rc-insights", GREEN),
        ("", WHITE),
        ("  No BI tool needed. Just: pip install rc-insights", DIM),
    ], title="Report Features", duration=6.0)
    t.add_transition()

    # --- Scene 11: Closing (5s) ---
    t.add_closing(5.0)

    # --- Fade out (1s) ---
    for fi in range(FPS):
        alpha = 1.0 - (fi / FPS)
        last = t.frames[-1]
        black = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        t.frames.append(Image.blend(black, last, alpha))

    output = os.path.join(os.path.dirname(__file__), "..", "assets", "demo.mp4")
    t.export(output)


if __name__ == "__main__":
    main()
