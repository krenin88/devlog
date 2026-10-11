# USER_GUIDE

에이전트가 대신할 수 없어 직접 처리해야 하는 일 목록입니다.

## Electronic Clam (eclam) 설정

- [x] **앱 실행 및 헬퍼 승인** (2026-10-12 완료, `helper: enabled` 확인) — 헬퍼가 켜져야 덮개를 닫아도 잠들지 않게 하는 기능과 안전 가드가 동작합니다.
  1. `open /Applications/ElectronicClam.app`
  2. 시스템 설정 → 일반 → 로그인 항목 및 확장 프로그램 → **Electronic Clam Helper** 켜기
  3. 확인: `eclam status` 실행 후 헬퍼 오류가 없는지 봅니다.
- [ ] **수동 `disablesleep 1` 정리 확인** — 헬퍼가 처음 뜰 때 기록 없는 `SleepDisabled=1`을 0으로 되돌립니다(의도된 동작). 이후 잠자기 제어는 eclam이 맡습니다.
  - 확인: `pmset -g | grep SleepDisabled` 가 `0` (keep-awake 꺼진 상태 기준)
  - 참고 (2026-10-12 해결됨, Terminal.app에 앱 관리 권한 허용 후 제거): 앱에 quarantine 속성이 남아 있으면 `eclam status`에 경고가 뜹니다. 헬퍼는 이미 동작하므로 급하지 않지만, 지우려면 `xattr -dr com.apple.quarantine /Applications/ElectronicClam.app` 후 앱을 다시 엽니다. Claude 앱 터미널에서는 macOS 앱 관리 보호 때문에 `Operation not permitted`로 실패합니다(2026-10-12 확인). 하려면 시스템 설정 → 개인정보 보호 및 보안 → 앱 관리에 Terminal.app을 허용한 뒤 Terminal.app에서 실행합니다.
- [ ] (선택) **Claude Code 훅 설치** — 에이전트 감지가 ~5초 폴링에서 즉시로 바뀝니다. `~/.claude/settings.json`에 훅이 추가됩니다.
  - 메뉴바 아이콘 우클릭 → Settings… → Agents → Advanced → **Install Claude hook**

## dev.to API 키

- [x] **API 키 발급 및 입력** — dev.to에 글을 게시하거나 조회하려면 필요합니다.
  1. https://dev.to/settings/extensions → **DEV Community API Keys**에서 설명을 입력하고 **Generate API Key**를 누릅니다.
  2. 프로젝트 루트 `.env`의 `DEVTO_API_KEY=` 뒤에 붙여 넣습니다. (`.env`는 git에 올라가지 않습니다.)
  - 2026-10-12 입력 확인됨 (계정 leejunhwa88, 읽기 전용 호출로 검증). main 체크아웃 `~/workspace/devlog/.env`에도 복사함.

## 블로그 게시 준비

- [x] **GitHub 저장소 만들고 push** (2026-10-12 완료, https://github.com/rogue1228/devlog) — 한글 글은 GitHub Pages로 게시합니다. 지금은 원격 저장소가 없습니다. 무료 플랜에서 Pages를 쓰려면 public이어야 합니다. 초안(`drafts/`)과 스캔 상태(`state/`)는 git에서 제외되어 올라가지 않습니다.
  1. `cd ~/workspace/devlog && gh repo create devlog --public --source . --push`
     (또는 Claude에게 "push 해줘"라고 요청)
- [ ] **GitHub Pages 켜기** — 시스템이 `_posts/`를 블로그로 렌더링합니다.
  1. GitHub 저장소 → Settings → Pages → Source: **Deploy from a branch**, Branch: **main** / **(root)** → Save
  2. 1~2분 뒤 `https://<github-username>.github.io/devlog/` 접속 확인
- [x] **예약 작업 1회 수동 실행** (2026-10-12 완료, 주제 후보 5개 생성 확인) — 첫 실행에서 도구 권한을 승인해 두면 이후 자동 실행이 권한 요청에서 멈추지 않습니다.
  1. Claude 앱 사이드바 → Scheduled → **devlog 블로그 주제 후보** → **Run now**
  2. 뜨는 권한 요청(Bash 실행 등)을 승인
- 참고: 예약 작업은 Claude 앱이 열려 있을 때만 실행됩니다. 닫혀 있으면 다음에 앱을 열 때 실행됩니다.
- [x] **GitHub Pages 켜기** (2026-10-12 완료, `gh api`로 main / root 설정) — https://rogue1228.github.io/devlog/

## Threads 자동 게시 준비

- [x] **Meta 앱과 토큰 발급** (2026-10-12 완료, 계정 leejunhwa88 읽기 전용 검증) — 홍보 글을 Threads에 자동으로 올리려면 필요합니다. 무료입니다.
  1. https://developers.facebook.com/apps → **앱 만들기** → 사용 사례에서 **Threads API 액세스** 선택
  2. 사용 사례 → 맞춤 설정 → 권한에 `threads_basic`, `threads_content_publish` 추가
  3. 앱 역할 → 역할 → **Threads 테스터 추가**에 본인 Threads 계정 입력 → Threads 앱(설정 → 계정 → 웹사이트 권한 → 초대)에서 수락
  4. 사용 사례 → 맞춤 설정 → 설정 → **사용자 토큰 생성기**에서 토큰 생성 (60일짜리 장기 토큰)
  5. `~/workspace/devlog/.env`의 `THREADS_ACCESS_TOKEN=` 뒤에 붙여 넣기
  6. Claude에게 "Threads 토큰 확인해줘"라고 요청 (읽기 전용 호출로 검증)
  - 참고: 토큰은 60일 동안 쓰지 않으면 만료됩니다. 게시할 때마다 자동 갱신되지만, 두 달 넘게 안 쓰면 4번부터 다시 하면 됩니다. 메뉴 이름은 Meta가 자주 바꿔서 조금 다를 수 있습니다.
- X는 자동 게시하지 않습니다. 블로그 게시 후 Claude가 보여 주는 문구를 직접 올립니다.

## 블로그 주소 바꾸기 (선택)

- [ ] (선택) **커스텀 도메인 연결** — 블로그 주소를 `rogue1228.github.io/devlog`에서 원하는 도메인으로 바꿉니다. 기존 github.io 주소로 들어오면 GitHub가 같은 경로의 새 도메인으로 301 리다이렉트하므로, dev.to와 SNS에 걸린 링크는 계속 동작합니다(다른 사이트에서 실측, 2026-10-12).
  1. 도메인 등록 업체(가비아, Cloudflare 등)에서 도메인을 삽니다. 유료입니다.
  2. GitHub → 프로필 Settings → Pages → **Add a domain**으로 도메인 소유를 먼저 인증합니다(TXT 레코드). 남이 내 도메인을 가로채는 것을 막습니다.
  3. 도메인 DNS에 레코드를 추가합니다. 서브도메인(예: `blog.example.com`)이면 `CNAME` → `rogue1228.github.io`, 루트 도메인이면 `A` 레코드 4개(185.199.108.153, .109.153, .110.153, .111.153).
  4. Claude에게 "도메인 연결해줘"라고 요청합니다. 저장소 Settings → Pages에 도메인을 넣고(`CNAME` 파일 커밋), dev.to 글의 `canonical_url`과 WORKFLOW를 새 주소로 맞춥니다.
  5. 인증서 발급 후 **Enforce HTTPS**를 켭니다.
- 참고: GitHub 사용자명을 바꾸는 방법으로는 주소를 바꾸지 않습니다. 저장소 주소는 리다이렉트되지만 `rogue1228.github.io` 블로그 주소는 리다이렉트된다는 근거가 없어, 기존 글 링크가 끊길 수 있습니다.
