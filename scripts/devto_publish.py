#!/usr/bin/env python3
# 영문 초안(front matter 포함 markdown)을 dev.to API로 게시하고 글 URL을 출력한다
"""Usage: devto_publish.py drafts/<slug>/en.md

front matter(title, published, tags, description)는 dev.to가 body_markdown 안에서 직접 해석한다.
API 키는 저장소 루트 .env 의 DEVTO_API_KEY 에서 읽는다.
"""
import json, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def api_key():
    env = ROOT / ".env"
    for line in env.read_text().splitlines() if env.exists() else []:
        k, _, v = line.partition("=")
        if k.strip() == "DEVTO_API_KEY" and v.strip():
            return v.strip()
    sys.exit(f"DEVTO_API_KEY가 {env} 에 없습니다.")


def main(path):
    body = Path(path).read_text()
    key = api_key()
    req = urllib.request.Request(
        "https://dev.to/api/articles",
        data=json.dumps({"article": {"body_markdown": body}}).encode(),
        headers={"api-key": key, "Content-Type": "application/json", "Accept": "application/vnd.forem.api-v1+json", "User-Agent": "devlog-publisher/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            print(json.load(r)["url"])
    except urllib.error.HTTPError as e:
        sys.exit(f"dev.to API {e.code}: {e.read().decode(errors='replace')}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
