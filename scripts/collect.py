#!/usr/bin/env python3
# 마지막 스캔 이후의 Claude 세션 입력과 ~/workspace git 커밋을 블로그 소재용 마크다운으로 요약한다
"""Usage: collect.py [--since ISO8601] [--mark] [--selftest]

--since 생략 시 state/last-scan, 그것도 없으면 48시간 전.
--mark  출력 후 state/last-scan 을 지금 시각으로 갱신.
"""
import json, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOME = Path.home()
PROJECTS = HOME / ".claude/projects"
WORKSPACE = HOME / "workspace"
STATE = Path(__file__).resolve().parent.parent / "state"
MAX_PROMPTS, MAX_CHARS = 20, 300


def load_excludes():
    f = STATE / "exclude.txt"
    if not f.exists():
        return []
    return [l.strip() for l in f.read_text().splitlines() if l.strip() and not l.startswith("#")]


def project_of(cwd):
    p = Path(cwd)
    try:
        return p.relative_to(WORKSPACE).parts[0]
    except (ValueError, IndexError):
        return p.name or str(p)


def user_texts(d):
    if d.get("type") != "user" or d.get("isMeta") or d.get("isSidechain"):
        return []
    c = d.get("message", {}).get("content")
    items = [c] if isinstance(c, str) else [i.get("text", "") for i in c or [] if isinstance(i, dict) and i.get("type") == "text"]
    # '<'로 시작하는 건 슬래시 커맨드·시스템 주입 태그라 사람 입력이 아니다
    return [t.strip() for t in items if t.strip() and not t.strip().startswith("<")]


def parse_session(path, since):
    title, cwd, prompts, first, last = None, None, [], None, None
    for line in path.open(errors="replace"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") == "custom-title":
            title = d.get("customTitle") or title
        ts = d.get("timestamp")
        if not ts or ts < since:
            continue
        cwd = d.get("cwd") or cwd
        for t in user_texts(d):
            first, last = first or ts, ts
            prompts.append(t[:MAX_CHARS].replace("\n", " "))
    return title, cwd, prompts, first, last


def sessions(since, excludes):
    out = []
    cutoff = datetime.fromisoformat(since.replace("Z", "+00:00")).timestamp()
    for f in sorted(PROJECTS.glob("*/*.jsonl")):
        if f.stat().st_mtime < cutoff:
            continue
        title, cwd, prompts, first, last = parse_session(f, since)
        if not prompts or not cwd:
            continue
        proj = project_of(cwd)
        if any(e in proj or e in cwd for e in excludes):
            continue
        out.append((proj, title or f.stem[:8], first, last, prompts))
    return sorted(out, key=lambda s: (s[0], s[2]))


def commits(since, excludes):
    out = []
    for repo in sorted(WORKSPACE.iterdir()):
        if not (repo / ".git").exists() or any(e in repo.name for e in excludes):
            continue
        log = subprocess.run(["git", "-C", str(repo), "log", "--all", "--no-merges", f"--since={since}",
                              "--date=short", "--format=%h %ad %s"], capture_output=True, text=True).stdout.strip()
        if log:
            out.append((repo.name, log))
    return out


def render(since, sess, comm):
    lines = [f"# 수집 결과 (since {since})", "", "## Claude 세션", ""]
    for proj, title, first, last, prompts in sess:
        lines.append(f"### {proj} — {title} ({first[:16]} ~ {last[:16]}, 입력 {len(prompts)}개)")
        lines += [f"- {p}" for p in prompts[:MAX_PROMPTS]]
        if len(prompts) > MAX_PROMPTS:
            lines.append(f"- … 외 {len(prompts) - MAX_PROMPTS}개")
        lines.append("")
    lines += ["## Git 커밋", ""]
    for name, log in comm:
        lines += [f"### {name}", "```", log, "```", ""]
    if not sess and not comm:
        lines.append("(새 기록 없음)")
    return "\n".join(lines)


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "s.jsonl"
        rows = [
            {"type": "custom-title", "customTitle": "테스트 세션"},
            {"type": "user", "timestamp": "2026-01-01T00:00:00Z", "cwd": "/x", "message": {"content": "옛날 입력"}},
            {"type": "user", "timestamp": "2026-02-01T00:00:00Z", "cwd": str(WORKSPACE / "app" / "sub"), "message": {"content": "새 입력"}},
            {"type": "user", "timestamp": "2026-02-01T00:01:00Z", "message": {"content": "<command-name>/x</command-name>"}},
            {"type": "user", "timestamp": "2026-02-01T00:02:00Z", "message": {"content": [{"type": "tool_result", "content": "x"}, {"type": "text", "text": "리스트 입력"}]}},
            {"type": "user", "timestamp": "2026-02-01T00:03:00Z", "isMeta": True, "message": {"content": "메타"}},
        ]
        f.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\nnot json\n")
        title, cwd, prompts, first, _ = parse_session(f, "2026-01-15T00:00:00Z")
        assert title == "테스트 세션", title
        assert prompts == ["새 입력", "리스트 입력"], prompts
        assert first == "2026-02-01T00:00:00Z"
        assert project_of(cwd) == "app"
    print("selftest ok")


def main(argv):
    if "--selftest" in argv:
        return selftest()
    since = argv[argv.index("--since") + 1] if "--since" in argv else None
    if not since and (STATE / "last-scan").exists():
        since = (STATE / "last-scan").read_text().strip()
    if not since:
        since = (datetime.now(timezone.utc) - timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ")
    excludes = load_excludes()
    print(render(since, sessions(since, excludes), commits(since, excludes)))
    if "--mark" in argv:
        STATE.mkdir(exist_ok=True)
        (STATE / "last-scan").write_text(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
