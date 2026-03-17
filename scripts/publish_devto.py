"""Publish the rc-insights blog post to Dev.to via the Forem API."""

import os
import sys
import json
import requests

API_KEY = os.environ.get("DEV_TO_API_KEY", "")
BLOG_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "blog-post.md")

TITLE = "Introducing rc-insights: The Missing Python SDK for RevenueCat's Charts API"
TAGS = ["python", "api", "opensource", "saas"]
CANONICAL_URL = "https://github.com/maruyamakoju/rc-insights/blob/master/docs/blog-post.md"
SERIES = None  # set to a string to group posts into a series


def main():
    if not API_KEY:
        print("Error: Set DEV_TO_API_KEY environment variable.")
        print("Get your key at: https://dev.to/settings/extensions")
        sys.exit(1)

    with open(BLOG_PATH, "r", encoding="utf-8") as f:
        body = f.read()

    # Strip the H1 title (Dev.to uses its own title field)
    lines = body.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    body_markdown = "\n".join(lines).strip()

    draft = "--publish" not in sys.argv
    payload = {
        "article": {
            "title": TITLE,
            "body_markdown": body_markdown,
            "published": not draft,
            "tags": TAGS,
            "canonical_url": CANONICAL_URL,
        }
    }
    if SERIES:
        payload["article"]["series"] = SERIES

    resp = requests.post(
        "https://dev.to/api/articles",
        headers={"api-key": API_KEY, "Content-Type": "application/json"},
        json=payload,
    )

    if resp.status_code in (200, 201):
        data = resp.json()
        status = "PUBLISHED" if not draft else "DRAFT"
        print(f"{status}: {data.get('url', 'unknown URL')}")
        print(f"ID: {data.get('id')}")
    else:
        print(f"Error {resp.status_code}: {resp.text[:500]}")
        sys.exit(1)


if __name__ == "__main__":
    print("Usage: DEV_TO_API_KEY=xxx python publish_devto.py [--draft|--publish]")
    print("  --draft   (default) Create as draft for review")
    print("  --publish Publish immediately")
    print()
    main()
