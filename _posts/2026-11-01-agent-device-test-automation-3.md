---
layout: post
title: "agent-device로 테스트 자동화 (3)"
description: "agent-device .ad 스크립트로 테스트 흐름 저장하고 다시 돌리기."
date: 2026-11-01
category: ai-agent
tags: [claude, agent-device, flutter, qa]
---

이 글은 agent-device의 `.ad` 스크립트로 테스트 흐름을 저장하고 다시 돌리는 방법을 Flutter 앱 기준으로 정리합니다. `.ad` 파일을 쓰는 법, 재생 전에 앱 상태를 맞추는 법, 재생이 멈췄을 때 보고를 읽고 고치는 법, 에이전트 QA의 토큰 비용을 다룹니다. 기준 버전은 agent-device 0.21.31(2026-10-25)입니다.

설치와 기본 사용 흐름은 [1편]({{ "/2026/10/25/agent-device-test-automation-1.html" | relative_url }}), 실기기 준비는 [2편]({{ "/2026/10/27/agent-device-test-automation-2.html" | relative_url }})에 있습니다.

## .ad란 무엇인가

에이전트가 앱을 확인할 때는 화면을 읽고, 다음에 누를 곳을 고르고, 결과를 다시 읽는 일을 반복합니다. 같은 흐름을 매번 이렇게 탐색하면 시간과 토큰이 계속 듭니다. `.ad`는 이 탐색 결과를 명령 목록으로 고정한 파일이고, `replay`는 그 목록을 위에서부터 차례로 실행합니다.

한 줄은 `<명령> [인자...] [플래그...]` 형태이고, 터미널에서 쓰는 agent-device 명령과 같습니다. 따옴표 규칙도 셸과 같아서, 공백이 든 선택자는 `'label="..."'`처럼 감쌉니다. 아래는 앱을 새로 연 뒤 첫 화면의 버튼을 누르고, 입력칸에 글을 넣고, 결과 화면을 확인하는 흐름의 앞부분입니다.

```text
# 첫 실행 흐름 — 앱 ID는 -e APP=로 받는다
open ${APP} --relaunch
wait 'label="<첫 화면 버튼>"' 30000
press 'label="<첫 화면 버튼>"'
fill 'id="find-input"' "<입력할 글>"
press 'label="<찾기 버튼>" role=button'
wait 'label="<결과 제목>"' 60000
wait text "<결과에 나와야 할 문구>" 10000
back
close
```

몇 가지를 적어 둡니다.

- **`#` 주석은 쓸 수 있습니다.** 문서에 명시돼 있지 않아서 첫 줄에 주석을 넣고 재생해 봤고, 그대로 통과했습니다.
- **앱 ID는 파일에 박지 않습니다.** `${APP}`로 두고 재생할 때 `-e APP=<번들 ID>`로 넘기면, 개발판과 출시판처럼 ID가 다른 빌드에 같은 파일을 쓸 수 있습니다.
- **`wait` 뒤의 숫자는 밀리초 단위 시간 제한입니다.** 네트워크나 모델 추론을 기다리는 단계는 길게 줍니다.
- **기기를 고르는 플래그는 파일에 넣지 않습니다.** `--platform`, `--serial`, `--device`와 `--settle`은 스크립트에 들어가지 않고, 재생 명령에 붙입니다.

`.ad`를 만드는 방법은 두 가지입니다. `open <번들 ID> --relaunch --save-script=<파일>.ad`로 녹화를 켜고 흐름을 조작한 뒤 `session save-script`로 저장할 수도 있고, 직접 써도 됩니다. 여기서 다룬 24단계 흐름은 에이전트가 손으로 먼저 통과시킨 흐름을 보고 직접 썼습니다.

## 재생 전에 '처음 실행' 상태 만들기

`replay`는 적힌 명령만 실행하고 앱 상태는 맞춰 주지 않습니다. 첫 실행 동의 창부터 확인하는 흐름이라면, 이전에 동의한 기록이 남은 앱에서는 2단계에서 바로 멈춥니다. 그래서 재생 전에 앱을 지우고 새로 설치하는 실행 스크립트를 따로 두었습니다.

```bash
# Android 에뮬레이터
adb -s <serial> uninstall <번들 ID>
adb -s <serial> install -r <apk 경로>
adb -s <serial> shell cmd locale set-app-locales <번들 ID> --locales en-US
agent-device replay <파일>.ad --platform android --serial <serial> -e APP=<번들 ID> --timeout 240000

# iOS 시뮬레이터
xcrun simctl uninstall <UDID> <번들 ID>
xcrun simctl install <UDID> <Runner.app 경로>
agent-device replay <파일>.ad --platform ios --udid <UDID> -e APP=<번들 ID> --timeout 300000
```

Android는 `set-app-locales`로 기기 언어는 그대로 두고 이 앱만 영어로 엽니다. iOS 시뮬레이터에는 앱별 언어를 바꾸는 명령을 쓰지 않았고, 시뮬레이터 언어 설정을 따라갑니다. `replay`는 기본 작업 시간이 60초라서, 흐름이 길면 `--timeout`으로 늘립니다.

앱을 지우면 그 앱의 데이터도 사라집니다. 그래서 실행 스크립트는 정해 둔 시험용 에뮬레이터(`adb -s <serial> emu avd name`으로 이름 확인)와 시뮬레이터 UDID만 받고, 그 밖의 기기나 다른 회사 앱 ID가 들어오면 종료 코드 2로 멈춥니다. 에뮬레이터 serial(`emulator-5554` 등)은 켠 순서로 정해져서 어느 AVD인지 알려 주지 않기 때문에 이름으로 확인했습니다.

이렇게 맞춘 뒤 24단계 흐름은 플랫폼마다 두 번씩 모두 `Replayed 24 steps`로 끝났습니다. Android 에뮬레이터는 8.8초와 9.4초, iOS 시뮬레이터는 13.9초와 14.0초였습니다.

## 재생이 멈췄을 때

재생이 중간에 막히면 `REPLAY_DIVERGENCE` 오류가 나옵니다. 보고에는 멈춘 단계 번호와 그 줄, 그때 화면에 있던 조작 가능한 요소 목록, 그 화면에서 쓸 수 있는 선택자 제안이 들어 있습니다. 고친 뒤 처음부터 다시 돌릴 필요가 없도록 `replay --from <단계> --plan-digest <값>`으로 이어서 돌리는 방법도 함께 알려 줍니다. 자동으로 고칠 수 없을 때는 `Repair hint: manual`이라고 표시됩니다.

**첫 실행 시스템 창.** Android에서 통과한 흐름을 iOS 시뮬레이터에서 처음 돌렸을 때 2단계에서 멈췄습니다.

```text
Error (REPLAY_DIVERGENCE): Replay failed at step 2 (wait "label=\"<첫 화면 버튼>\"" 30000): wait timed out for selector: ...
Current surface: Allow "<앱 이름>" to track your activity across other companies' apps ...
```

보고의 `Current surface`에 앱 추적 허용(ATT) 창이 떠 있었습니다. iOS에서만 첫 실행에 뜨는 시스템 창이라 Android 기준으로 쓴 흐름에는 그 단계가 없었습니다. `agent-device alert dismiss`로 창을 닫은 뒤 다시 재생하자 이 단계는 지나갔습니다. 실행 스크립트가 처리하지 않으므로, 이 창이 뜨는 빌드에서는 재생 전에 닫아 줘야 합니다.

**플랫폼마다 다른 입력칸 역할 이름.** 그다음은 5단계 `fill`에서 멈췄습니다. 처음 쓴 선택자는 `role=text-field`였고 Android에서는 맞았지만, iOS 시뮬레이터는 같은 입력칸을 라벨이 붙은 `other` 요소로 보여 줬습니다. 두 플랫폼에 같이 맞는 선택자를 찾으려고 아래 순서로 바꿔 봤습니다.

1. `editable=true` — Android는 통과, iOS는 `Selector did not match`
2. `role=textfield || role=text-field` — `||`는 보고의 선택자 제안에 나온 '또는' 문법입니다. iOS에서는 역시 맞지 않았습니다.
3. Flutter 위젯에 `Semantics(identifier:)` 추가 — 두 플랫폼 모두 통과

마지막 방법은 앱 코드 한 줄입니다. 입력칸을 감싼 기존 `Semantics`에 `identifier: 'find-input'`을 더했고, 화면은 바뀌지 않습니다. 선택자는 `id="find-input"`이 됩니다. 1편에서 적었듯 Flutter의 `Key`는 접근성 트리에 나오지 않으므로, 두 플랫폼에서 같은 스크립트를 돌리려면 `identifier`를 붙이는 쪽이 확실합니다.

## 토큰 비용과 줄이는 규칙

`.ad`를 쓰게 된 이유는 토큰 비용이었습니다. 에이전트 QA 비용의 대부분은 출력이 아니라 캐시 읽기였습니다. 캐시 읽기는 에이전트가 응답할 때마다 앞선 대화를 다시 읽는 양입니다. 실기기에서 앱 두 개를 처음 확인한 약 40분 동안 응답 121번, 출력 77,985토큰, 캐시 읽기 30,225,404토큰이 나왔고, 응답 한 번에 약 25만 토큰을 다시 읽은 셈입니다.

QA 에이전트는 이미 Sonnet이어서 모델이 원인은 아니었습니다. 같은 구간에 스크린샷 11장을 대화로 읽어 들였고, 맥락이 커질수록 응답마다 다시 읽는 양이 불었습니다. 그래서 QA 에이전트 규칙에 다음 다섯 가지를 넣었습니다.

1. 처음 통과한 흐름은 `.ad`로 저장하고, 다음부터는 `replay`로 돌린다. 막히면 divergence 보고로 그 단계만 고친다.
2. 조작은 `--settle`로 하고 돌아온 차이만 본다. 전체 화면 트리는 읽지 않는다.
3. 스크린샷은 파일로만 저장하고, 대화에는 항목당 한 장 이하만 읽는다.
4. 앱 하나, 확인 항목 하나 단위로 세션을 끊는다. 응답 40번을 넘으면 끊을 때로 본다.
5. 로그와 빌드 출력은 `grep`·`tail`로 필요한 줄만 읽는다.

규칙을 넣은 뒤의 묶음(에뮬레이터 확인 세 건, iPhone 시도, Android 실기기, 약 30분)은 응답 105번, 출력 44,113토큰, 캐시 읽기 19,171,162토큰이었고, 응답당 캐시 읽기는 약 18만 토큰입니다. 확인한 항목이 달라서 두 숫자를 바로 비교할 수는 없고, 응답 40번 기준도 지키지 못했습니다. `.ad`를 들인 뒤의 토큰은 아직 따로 재지 않았고, 실기기에서의 재생과 CI 실행도 해 보지 않았습니다.

## 참고

- agent-device 저장소: <https://github.com/callstack/agent-device>
- agent-device 에이전트 설정 문서: <https://oss.callstack.com/agent-device/docs/agent-setup>
- Flutter `Semantics.identifier`: <https://api.flutter.dev/flutter/semantics/SemanticsProperties/identifier.html>
