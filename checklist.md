# Checklist — devlog 블로그 자동 초안

- [ ] 저장소 골격: `_config.yml`(Jekyll), `_posts/`, `drafts/`, `state/`, `.gitignore`에 graft 항목 병합
- [ ] `scripts/collect.py` — 마지막 스캔 이후 Claude 세션 요약 + ~/workspace git log 수집 → verify: self-check 통과, 실제 실행 출력 확인
- [ ] `scripts/devto-publish.sh` — en.md를 dev.to API로 게시 → verify: 키 없이 실행 시 명확한 오류
- [ ] `WORKFLOW.md` — 수집 → 주제 제안 → 한글 초안 → 영문 → 승인 → 게시 절차와 개인정보 규칙
- [ ] 이 브랜치를 main에 반영 (예약 작업은 `~/workspace/devlog` main 체크아웃에서 실행)
- [ ] 예약 작업 등록: 이틀마다 09:00, WORKFLOW.md 1단계 실행
- [ ] USER_GUIDE.md: GitHub repo 생성·push·Pages 활성화, dev.to 키
- [ ] 1회 수동 실행으로 주제 후보가 나오는지 확인
