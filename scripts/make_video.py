"""Generate a terminal-style demo video for rc-insights using Pillow + ffmpeg."""

import os
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Video settings
WIDTH, HEIGHT = 1280, 720
FPS = 10
BG_COLOR = (15, 15, 35)
TEXT_COLOR = (224, 224, 224)
GREEN = (29, 185, 84)
CYAN = (0, 212, 255)
DIM = (136, 136, 136)
YELLOW = (255, 214, 10)
PROMPT_COLOR = GREEN

# Try to find a monospace font
FONT_SIZE = 18
FONT_PATHS = [
    "C:/Windows/Fonts/consola.ttf",       # Consolas (Windows)
    "C:/Windows/Fonts/cour.ttf",          # Courier New
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]

font = None
for fp in FONT_PATHS:
    if os.path.exists(fp):
        font = ImageFont.truetype(fp, FONT_SIZE)
        break
if font is None:
    font = ImageFont.load_default()

TITLE_FONT = None
for fp in FONT_PATHS:
    if os.path.exists(fp):
        TITLE_FONT = ImageFont.truetype(fp, 28)
        break
if TITLE_FONT is None:
    TITLE_FONT = font

LINE_HEIGHT = 24
MARGIN_X = 30
MARGIN_Y = 20


def make_frame(lines, title=None):
    """Create a single frame with terminal-style text."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Window decorations
    draw.rounded_rectangle([10, 10, WIDTH - 10, 45], radius=8, fill=(30, 30, 60))
    # Traffic light dots
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse([24 + i * 22, 20, 38 + i * 22, 34], fill=color)

    # Title
    if title:
        draw.text((WIDTH // 2 - len(title) * 5, 18), title, fill=DIM, font=font)

    y = 55 + MARGIN_Y
    for line_data in lines:
        if isinstance(line_data, str):
            text, color = line_data, TEXT_COLOR
        elif isinstance(line_data, tuple) and len(line_data) == 2:
            text, color = line_data
        else:
            continue

        if text == "---":
            y += LINE_HEIGHT // 2
            continue

        draw.text((MARGIN_X, y), text, fill=color, font=font)
        y += LINE_HEIGHT

    return img


# Define scenes as (duration_seconds, title, lines)
scenes = [
    # Scene 1: Title
    (3, "rc-insights", [
        "",
        "",
        ("  rc-insights", CYAN),
        ("  ─────────────────────────────────────", DIM),
        ("  Python SDK + CLI for RevenueCat Charts API v2", TEXT_COLOR),
        "",
        ("  • Typed SDK for all 21 chart endpoints", TEXT_COLOR),
        ("  • CLI with Rich terminal output", TEXT_COLOR),
        ("  • HTML report generator with Plotly charts", TEXT_COLOR),
        ("  • Auto-generated subscription insights", TEXT_COLOR),
        "",
        ("  Built by Claude (AI Agent) for @maruyamakoju", DIM),
    ]),

    # Scene 2: Installation
    (3, "Installation", [
        ("$ pip install rc-insights", PROMPT_COLOR),
        ("Collecting rc-insights", DIM),
        ("  Downloading rc_insights-0.1.0-py3-none-any.whl", DIM),
        ("Installing collected packages: rc-insights", DIM),
        ("Successfully installed rc-insights-0.1.0", GREEN),
        "",
        ("$ export REVENUECAT_API_KEY=sk_...", PROMPT_COLOR),
        ("$ export REVENUECAT_PROJECT_ID=proj...", PROMPT_COLOR),
        "",
        ("  ✓ One pip install. Two env vars. Ready.", GREEN),
    ]),

    # Scene 3: Overview command
    (4, "rc-insights overview", [
        ("$ rc-insights overview", PROMPT_COLOR),
        "",
        ("┌─────────────────────────────────────────────┐", CYAN),
        ("│           RevenueCat Overview                │", CYAN),
        ("├──────────────────────┬──────────┬────────────┤", CYAN),
        ("│ Metric               │    Value │ Period     │", CYAN),
        ("├──────────────────────┼──────────┼────────────┤", CYAN),
        ("│ Active Trials        │       65 │ P0D        │", TEXT_COLOR),
        ("│ Active Subscriptions │    2,529 │ P0D        │", TEXT_COLOR),
        ("│ MRR                  │$4,557.00 │ P28D       │", GREEN),
        ("│ Revenue              │$5,105.00 │ P28D       │", GREEN),
        ("│ New Customers        │    1,572 │ P28D       │", TEXT_COLOR),
        ("│ Active Users         │   13,957 │ P28D       │", TEXT_COLOR),
        ("└──────────────────────┴──────────┴────────────┘", CYAN),
        "",
        ("  All your key metrics. One command.", DIM),
    ]),

    # Scene 4: Chart query
    (4, "rc-insights chart mrr", [
        ("$ rc-insights chart mrr --start 2025-01-01 --end 2025-12-31", PROMPT_COLOR),
        "",
        ("             MRR (month)                      ", CYAN),
        ("┌────────────┬───────────┐", CYAN),
        ("│ Date       │       MRR │", CYAN),
        ("├────────────┼───────────┤", CYAN),
        ("│ 2025-01-01 │ $4,505.42 │", TEXT_COLOR),
        ("│ 2025-02-01 │ $4,583.13 │", TEXT_COLOR),
        ("│ 2025-03-01 │ $4,636.80 │", TEXT_COLOR),
        ("│ ...        │       ... │", DIM),
        ("│ 2025-10-01 │ $4,322.58 │", TEXT_COLOR),
        ("│ 2025-11-01 │ $4,421.66 │", TEXT_COLOR),
        ("│ 2025-12-01 │ $4,411.46 │", TEXT_COLOR),
        ("└────────────┴───────────┘", CYAN),
        "",
        ("  Use -j for JSON output → pipe to jq, pandas, etc.", DIM),
    ]),

    # Scene 5: Python SDK
    (4, "Python SDK", [
        (">>> from rc_insights import RCInsights", YELLOW),
        (">>> rc = RCInsights(api_key='sk_...', project_id='proj...')", YELLOW),
        "",
        (">>> overview = rc.overview()", YELLOW),
        (">>> print(f\"MRR: {overview['mrr'].formatted_value}\")", YELLOW),
        ("MRR: $4,557.00", GREEN),
        "",
        (">>> mrr = rc.chart('mrr', start_date='2025-01-01',", YELLOW),
        ("...                end_date='2025-12-31')", YELLOW),
        (">>> for date, value in mrr.to_series()[-3:]:", YELLOW),
        ("...     print(f'  {date}: ${value:,.2f}')", YELLOW),
        ("  2025-10-01: $4,322.58", TEXT_COLOR),
        ("  2025-11-01: $4,421.66", TEXT_COLOR),
        ("  2025-12-01: $4,411.46", TEXT_COLOR),
        "",
        ("  Typed dataclasses. No JSON wrangling.", DIM),
    ]),

    # Scene 6: Report generation
    (4, "Report Generator", [
        ("$ rc-insights report -o health_report.html", PROMPT_COLOR),
        ("Fetching overview metrics...", CYAN),
        ("Fetching health charts...", CYAN),
        ("  ✓ mrr: 24 data points", GREEN),
        ("  ✓ revenue: 24 data points", GREEN),
        ("  ✓ churn: 24 data points", GREEN),
        ("  ✓ actives: 24 data points", GREEN),
        ("  ✓ trial_conversion_rate: 23 data points", GREEN),
        ("  ✓ ltv_per_paying_customer: 24 data points", GREEN),
        ("Generating report...", CYAN),
        ("Report saved to health_report.html", GREEN),
        "",
        ("  Interactive Plotly charts + auto-generated insights", DIM),
        ("  MRR grew 7.7% • Active subs +143 • Retention is king", CYAN),
    ]),

    # Scene 7: Closing
    (3, "Get Started", [
        "",
        ("  pip install rc-insights", GREEN),
        "",
        ("  GitHub:  github.com/maruyamakoju/rc-insights", CYAN),
        "",
        ("  21 chart types • Segmentation • Filtering", TEXT_COLOR),
        ("  CLI • Python SDK • HTML Reports", TEXT_COLOR),
        "",
        ("  ─────────────────────────────────────", DIM),
        ("  Built by Claude (AI Agent, Anthropic)", DIM),
        ("  Operator: @maruyamakoju", DIM),
        ("  Powered by RevenueCat Charts API v2", DIM),
        "",
        ("  ★ Star the repo. Open an issue. Build something cool.", YELLOW),
    ]),
]


def main():
    tmpdir = tempfile.mkdtemp(prefix="rc_video_")
    print(f"Rendering frames to {tmpdir}")

    frame_num = 0
    for duration, title, lines in scenes:
        frame = make_frame(lines, title=title)
        num_frames = int(duration * FPS)
        for i in range(num_frames):
            path = os.path.join(tmpdir, f"frame_{frame_num:05d}.png")
            frame.save(path)
            frame_num += 1

    print(f"Total frames: {frame_num}")

    output = os.path.join(os.path.dirname(__file__), "..", "assets", "demo.mp4")
    os.makedirs(os.path.dirname(output), exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(tmpdir, "frame_%05d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "23",
        output,
    ]
    print(f"Running ffmpeg...")
    subprocess.run(cmd, check=True)
    print(f"Video saved to {output}")

    # Cleanup
    import shutil
    shutil.rmtree(tmpdir)


if __name__ == "__main__":
    main()
