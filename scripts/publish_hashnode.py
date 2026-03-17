"""Publish the rc-insights blog post to Hashnode via their GraphQL API."""

import os
import sys
import json
import requests

API_KEY = os.environ.get("HASHNODE_API_KEY", "")
PUBLICATION_ID = os.environ.get("HASHNODE_PUBLICATION_ID", "")
BLOG_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "blog-post.md")

TITLE = "Introducing rc-insights: The Missing Python SDK for RevenueCat's Charts API"
SLUG = "rc-insights-revenuecat-charts-api-python-sdk"
TAGS = []  # Hashnode tag IDs — find via their API or dashboard
SUBTITLE = "How I built a subscription analytics toolkit in 48 hours — and what Dark Noise's real data taught me."


def main():
    if not API_KEY:
        print("Error: Set HASHNODE_API_KEY environment variable.")
        print("Get your token at: https://hashnode.com/settings/developer")
        sys.exit(1)
    if not PUBLICATION_ID:
        print("Error: Set HASHNODE_PUBLICATION_ID environment variable.")
        print("Find it in your Hashnode blog dashboard URL.")
        sys.exit(1)

    with open(BLOG_PATH, "r", encoding="utf-8") as f:
        body = f.read()

    lines = body.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    content_markdown = "\n".join(lines).strip()

    query = """
    mutation PublishPost($input: PublishPostInput!) {
        publishPost(input: $input) {
            post {
                id
                url
                title
            }
        }
    }
    """

    variables = {
        "input": {
            "title": TITLE,
            "subtitle": SUBTITLE,
            "slug": SLUG,
            "contentMarkdown": content_markdown,
            "publicationId": PUBLICATION_ID,
            "tags": [{"id": t} for t in TAGS] if TAGS else [],
        }
    }

    resp = requests.post(
        "https://gql.hashnode.com",
        headers={
            "Authorization": API_KEY,
            "Content-Type": "application/json",
        },
        json={"query": query, "variables": variables},
    )

    if resp.status_code == 200:
        data = resp.json()
        if "errors" in data:
            print(f"GraphQL errors: {json.dumps(data['errors'], indent=2)}")
            sys.exit(1)
        post = data.get("data", {}).get("publishPost", {}).get("post", {})
        print(f"Published: {post.get('url', 'unknown')}")
        print(f"ID: {post.get('id')}")
    else:
        print(f"Error {resp.status_code}: {resp.text[:500]}")
        sys.exit(1)


if __name__ == "__main__":
    print("Usage: HASHNODE_API_KEY=xxx HASHNODE_PUBLICATION_ID=yyy python publish_hashnode.py")
    print()
    main()
