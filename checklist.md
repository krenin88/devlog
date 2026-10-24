# Checklist — devlog 블로그 자동 초안

- [x] 저장소 골격: `_config.yml`(Jekyll), `_posts/`, `drafts/`, `state/`, `.gitignore`에 graft 항목 병합
- [x] `scripts/collect.py` — 마지막 스캔 이후 Claude 세션 요약 + ~/workspace git log 수집 → verify: self-check 통과, 실제 실행 출력 확인
- [x] `scripts/devto_publish.py` — en.md를 dev.to API로 게시 → verify: /users/me 읽기 호출로 키 검증 (실제 게시는 첫 승인 때)
- [x] `WORKFLOW.md` — 수집 → 주제 제안 → 한글 초안 → 영문 → 승인 → 게시 절차와 개인정보 규칙
- [x] 이 브랜치를 main에 반영 (예약 작업은 `~/workspace/devlog` main 체크아웃에서 실행)
- [x] 예약 작업 등록: 이틀마다 09:00, WORKFLOW.md 1단계 실행
- [x] USER_GUIDE.md: GitHub repo 생성·push·Pages 활성화, dev.to 키
- [x] Threads 토큰 입력 후 읽기 전용 검증 (`GET /v1.0/me`)
- [x] `scripts/threads_publish.py` + WORKFLOW 5단계(홍보) — verify: 500자 초과·토큰 없음 오류 확인
- [x] 1회 수동 실행으로 주제 후보가 나오는지 확인

# Checklist — 블로그 디자인 (B안 개발 노트, 2026-10-12)

- [x] 시안 3개 제시 → 사용자 B안 선택
- [x] 문구 확정: 제목 "Krenin의 devlog", 소개, About 본문, GitHub·Threads 링크 미노출
- [x] minima 덮어쓰기: `_includes/head.html`·`header.html`·`footer.html`, `_layouts/home.html`·`post.html`, `assets/main.scss`
- [x] `about.md` 추가, `_config.yml` title·description·header_pages 갱신 (timezone·exclude 유지)
- [x] 로컬 빌드 → verify: 첫 글 주소 `/2026/10/12/lizard-ranch-demo.html` 그대로, 경고 없음
- [x] 화면 확인: 데스크톱·모바일 너비, 라이트·다크, 코드 블록·표 → 스크린샷
- [x] 사용자 승인 → main ff-merge → push → Pages 결과 확인 (2026-10-12, c982230 빌드 성공, 홈·About·첫 글·feed 200)

# Checklist — 글에 이미지 넣기 (다음 작업, 2026-10-12 사용자 요청)

- [ ] WORKFLOW.md 2단계(한글 초안)에 이미지 고르기 단계 추가 — 초안 쓸 때 글에 맞는 이미지를 후보로 제안하고 사용자가 고른다
- [ ] 이미지 위치·형식 정하기 — 예: `assets/images/<slug>/`, 본문은 `{{ "/assets/images/..." | relative_url }}`, alt 문구 필수, 용량 줄이기
- [ ] dev.to 영문판 처리 정하기 — dev.to는 상대 경로를 못 읽으므로 Pages 절대 주소를 쓰거나 dev.to에 업로드
- [x] 이미지 출처 규칙 — 실제 스크린샷만, 필요한 만큼(최소 장수 없음), 개인정보(이메일·경로·키)가 보이는 화면은 가리기, alt 필수 (2026-10-25, WORKFLOW.md 2단계 "글 구조")
- [ ] 디자인 확인 — 본문 이미지 폭·여백·캡션, 모바일, 다크 모드

# Checklist — SEO 설정 (2026-10-25, github.io 주소로 Google·Naver 등록)

- [ ] `_config.yml`에 `jekyll-sitemap` 추가 → verify: push 뒤 `/devlog/sitemap.xml` 200, 첫 글 주소 포함
- [ ] `_config.yml`에 `author` 추가 → verify: 글 JSON-LD에 author 나옴
- [x] 인증 메타 자리: Google은 `webmaster_verifications.google`, Naver는 `head.html`의 `naver-site-verification` (값은 사용자가 받아 오면 넣음)
- [x] WORKFLOW.md 2단계 front matter에 `description` 추가 (검색 결과 요약문)
- [x] 사용자 할 일 이슈: Search Console·서치어드바이저 속성 추가, 인증 코드 전달, 사이트맵 제출 (krenin88/devlog#2)
- [ ] 인증 코드 넣고 push → 사용자가 두 콘솔에서 인증·사이트맵 제출 → verify: 콘솔에서 사이트맵 "성공"
- 보류: 기본 OG 이미지(이미지 규칙이 정해진 뒤), robots.txt(프로젝트 사이트라 루트 `krenin88.github.io/robots.txt`에 둘 수 없음 — 404면 크롤러는 전부 허용으로 봄)
