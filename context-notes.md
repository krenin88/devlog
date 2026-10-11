# Context Notes

## 목적 (2026-10-12)
Claude로 앱을 개발한 내역을 블로그 글로 만든다. 한글은 GitHub(이 devlog 저장소 + GitHub Pages), 영문은 dev.to.
이틀마다 세션·저장소 기록을 훑어 주제 후보를 보내고 → 사용자가 고른 주제로 초안 → 사용자 승인 시에만 게시.

## 결정
- **전송 채널 = Claude 앱 예약 작업.** 데이터(~/.claude/projects, ~/workspace)가 로컬이라 로컬 실행 필수. 예약 실행 세션에 답장하면 선택→초안→승인→게시가 한 대화에서 이어짐. 메일은 답장으로 흐름을 이어 갈 수 없고, 텔레그램은 봇 토큰·상시 수신 데몬·채팅발 게시 권한이 추가로 필요. 한계: 앱이 열려 있어야 실행(닫혀 있으면 다음 실행 시).
- **수집 범위 = ~/workspace 전체 + 모든 Claude 세션.** 빼고 싶은 프로젝트는 `state/exclude.txt`.
- **영문 = 한글 확정 후 dev.to 톤으로 현지화.** (전역 규칙: 한국어 먼저 확정)
- **주기 = cron `0 9 */2 * *`.** 월말·월초에는 하루 간격이 될 수 있음(허용).
- **세션 원문은 수집 스크립트로 요약해 읽는다.** jsonl 하나가 MB 단위라 통째로 읽으면 토큰 낭비. 사용자 입력 텍스트·세션 제목·cwd·기간만 뽑는다.
- **게시는 항상 명시적 승인 후.** 한글 게시 = `_posts/` 커밋 + push, 영문 = dev.to API.
- **개인정보:** 초안에 키·토큰·이메일·고객/회사 실명·절대 경로 사용자명 등 넣지 않음.
- 예약 작업은 worktree가 아닌 main 체크아웃 `/Users/junhwa/workspace/devlog`에서 동작.
- **`drafts/`·`state/`는 git 제외.** Pages는 public 저장소라 승인 전 초안·제안 목록·제외 프로젝트 이름이 공개되면 안 됨. 대신 로컬 전용이라 백업은 없음.
- **dev.to 요청에 User-Agent 필수.** 없으면 빈 본문 403 (2026-10-12 확인). 키 검증은 `GET /api/users/me`로 함 — 테스트 게시는 계정에 글이 생기므로 하지 않음.
- **main 체크아웃 반영 시** graft가 만든 미추적 `.gitignore`·`.ignore`를 scratchpad로 옮기고 ff-merge. 내용은 커밋된 파일에 포함됨. `.env`는 worktree에서 main으로 복사(chmod 600).
- **Threads = API 자동, X = 문구만 (2026-10-12 사용자 결정).** X API는 무료 등급이 없고 링크 포함 글이 건당 약 $0.20(외부 자료 기준). 승인 단계가 있어 수동 복붙 비용이 작음. 게시가 잦아지면 X API 재검토.
- **Threads 토큰은 게시 때마다 갱신해 .env에 다시 씀.** 장기 토큰은 60일 미사용 시 만료, 발급 24시간 이내엔 갱신 거절 → 그땐 기존 토큰 사용.
- **GitHub:** https://github.com/rogue1228/devlog (public), Pages = main / root, https://rogue1228.github.io/devlog/
- **`.env`는 main 체크아웃(`~/workspace/devlog/.env`)이 원본.** 사용자가 앱 파일 창에서 worktree 쪽 `.env`를 편집하는 일이 두 번 있었음 — 키 확인 시 양쪽을 다 보고 main으로 옮길 것.
- **Jekyll `timezone: Asia/Seoul` 필수.** 없으면 UTC 기준이라 KST 새벽에 오늘 날짜 글을 올리면 미래 글로 보고 빌드에서 빠짐 (2026-10-12 첫 게시 때 추가).
- **첫 글 게시 (2026-10-12):** dev.to·Pages 게시 검증 완료. Threads 게시는 같은 날 이미 SNS에 올려 생략 — `threads_publish.py` 실제 게시는 아직 미검증.

## 블로그 디자인 (2026-10-12)
- **B안 "개발 노트" 선택.** 모눈 배경, 모노 날짜 열, 코드 블록 파일명 바(언어 표시), `#태그`. 시안 3개(A 미니멀, B 개발 노트, C 도트) 중 사용자 선택.
- **문구 (사용자 확정):** title "Krenin의 devlog", description "앱과 게임을 Claude로 만듭니다. 개발하면서 겪은 일을 기록합니다." (띄어쓰기만 교정), About은 사용자가 쓴 문장 그대로. GitHub·Threads 링크는 넣지 않음. 메뉴는 About · dev.to (EN).
- **방식 = minima 유지 + 일부 덮어쓰기.** `theme: minima`를 두면 jekyll-seo-tag·jekyll-feed가 그대로 동작. CSS는 `assets/main.scss`를 통째로 새로 써서 minima sass를 import하지 않음(덮어쓰기 충돌 방지). `default.html`·`page.html`은 테마 것을 그대로 씀.
- **글꼴:** 본문 IBM Plex Sans KR, 코드·날짜 IBM Plex Mono (Google Fonts). 한글 웹폰트는 무거워서 `display=swap`.
- **permalink 미변경.** 기존 기본값(`/:categories/:year/:month/:day/:title:output_ext`) 유지.
- **닉네임·도메인 조사 결과:** GitHub 사용자명을 바꾸면 `rogue1228.github.io` 주소가 사라짐(문서에 Pages 리다이렉트 언급 없음, 저장소 URL만 리다이렉트). 커스텀 도메인은 github.io 주소를 경로 유지한 채 301 리다이렉트함 — `jekyll.github.io/jekyll/docs/installation/` → `jekyllrb.com/docs/installation/` 실측(2026-10-12). 따라서 주소를 바꾸려면 사용자명 변경이 아니라 커스텀 도메인.
- **로컬 미리보기:** scratchpad에 `github-pages` gem(223, Jekyll 3.9, minima 2.5.1) 설치. Ruby 4라 `csv`·`base64`·`bigdecimal`·`logger`·`ostruct` gem 추가 필요. 실제 Pages는 Jekyll 3.10.
