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
