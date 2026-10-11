#!/usr/bin/env python3
# 홍보 문구 파일을 Threads에 텍스트 글로 게시하고 글 URL을 출력한다
"""Usage: threads_publish.py drafts/<slug>/threads.txt

.env 의 THREADS_ACCESS_TOKEN 을 쓴다. 장기 토큰은 60일 동안 안 쓰면 만료되므로
게시할 때마다 갱신을 시도하고, 새 토큰을 .env 에 다시 쓴다.
"""
import json, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"
API = "https://graph.threads.net"
MAX_CHARS = 500


def read_token():
    for line in ENV.read_text().splitlines() if ENV.exists() else []:
        k, _, v = line.partition("=")
        if k.strip() == "THREADS_ACCESS_TOKEN" and v.strip():
            return v.strip()
    sys.exit(f"THREADS_ACCESS_TOKEN이 {ENV} 에 없습니다.")


def call(method, path, **params):
    url = f"{API}{path}"
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        url, data = f"{url}?{data.decode()}", None
    req = urllib.request.Request(url, data=data, method=method, headers={"User-Agent": "devlog-publisher/1.0"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Threads API {e.code} ({path}): {e.read().decode(errors='replace')}")


def refresh(token):
    # 발급 24시간 이내 토큰은 갱신이 거절된다 — 그땐 기존 토큰으로 계속 진행
    url = f"{API}/refresh_access_token?" + urllib.parse.urlencode({"grant_type": "th_refresh_token", "access_token": token})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "devlog-publisher/1.0"})) as r:
            new = json.load(r)["access_token"]
    except (urllib.error.HTTPError, KeyError):
        return token
    lines = [f"THREADS_ACCESS_TOKEN={new}" if l.split("=", 1)[0].strip() == "THREADS_ACCESS_TOKEN" else l
             for l in ENV.read_text().splitlines()]
    ENV.write_text("\n".join(lines) + "\n")
    return new


def main(path):
    text = Path(path).read_text().strip()
    if len(text) > MAX_CHARS:
        sys.exit(f"{len(text)}자 — Threads 한도 {MAX_CHARS}자를 넘습니다.")
    token = refresh(read_token())
    container = call("POST", "/v1.0/me/threads", media_type="TEXT", text=text, access_token=token)["id"]
    time.sleep(5)  # Meta 권장: 컨테이너 생성 후 잠시 대기
    post = call("POST", "/v1.0/me/threads_publish", creation_id=container, access_token=token)["id"]
    print(call("GET", f"/v1.0/{post}", fields="permalink", access_token=token)["permalink"])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
