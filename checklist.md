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
- [ ] 사용자 승인 → main ff-merge → push → Pages 결과 확인
