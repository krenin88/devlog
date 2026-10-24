---
layout: post
title: "agent-device로 테스트 자동화 (1)"
description: "Flutter 앱 테스트에 agent-device를 고른 이유와 Claude Code 설치, 기본 사용 흐름, Flutter에서 주의할 점을 정리합니다."
date: 2026-10-25
category: ai-agent
tags: [claude, agent-device, flutter, qa]
---

agent-device는 AI 에이전트가 iOS·Android 앱을 직접 조작하고 화면을 확인하게 해 주는 Callstack의 오픈소스 도구입니다. 이 글은 Flutter 앱 테스트에 agent-device를 고른 이유, Claude Code에 붙이는 설치 과정, 기본 사용 흐름, Flutter에서 주의할 점을 정리합니다. 기준 버전은 0.21.31(2026-10-24)입니다.

## 왜 agent-device인가

Flutter는 한 코드로 Android와 iOS 앱을 함께 만듭니다. 그래서 기기 테스트 도구도 iOS까지 다뤄야 했습니다. 처음 검토한 Google Artemis는 자연어로 앱을 테스트하는 에이전트지만 Android만 지원하고, iOS는 로드맵에만 올라 있습니다.

함께 비교한 후보는 다음과 같습니다.

- **mobile-mcp**는 iOS·Android의 탭·스크린샷·접근성 트리를 MCP(AI가 외부 도구를 부르는 연결 방식)로 제공합니다. 다만 세션, 리플레이, 증거 저장이 없어서 확인한 흐름을 CI로 넘기기 어렵습니다.
- **Maestro**는 YAML로 흐름을 고정하는 E2E 테스트 프레임워크이고 MCP도 있습니다. 에이전트가 화면을 탐색하는 쪽보다 정해진 흐름을 반복하는 회귀 테스트에 맞습니다.
- **Arbigent**는 Maestro 위에 얹은 AI 에이전트입니다. 작성자 스스로 속도 1/5, 신뢰성 3/5로 평가했고 YAML 형식이 바뀌는 중이었습니다.
- **상용 서비스**(Drizz, Minitap 등)는 실기기 팜과 자연어 에이전트를 묶어 팔지만, 공개된 자료가 벤더 자료뿐이라 비용과 품질을 확인할 수 없었습니다.

agent-device는 iOS·Android의 시뮬레이터와 실기기를 한 도구로 다루고, 문서에 Flutter 지원이 명시돼 있습니다. CLI와 MCP를 둘 다 제공하고, 확인한 흐름을 `.ad` 스크립트로 저장해 다시 돌리거나 Maestro YAML로 내보낼 수 있습니다. 라이선스는 MIT입니다.

## 설치

CLI를 전역으로 설치하고 환경을 점검합니다.

```bash
npm i -g agent-device@latest
agent-device doctor
```

`doctor`는 연결된 기기, 툴체인, 개발 서버 상태를 점검합니다. 이번 환경에서는 쓰지 않는 플랫폼(HarmonyOS, Vega) 경고만 남고 통과했습니다.

Claude Code에는 MCP 서버로 등록합니다. `-s user`로 등록하면 모든 프로젝트에서 같은 도구가 보입니다.

```bash
claude mcp add -s user agent-device -- agent-device mcp
```

agent-device 저장소에는 에이전트용 스킬 세 개(`agent-device`, `ios-simulator`, `android-emulator`)가 있습니다. 공식 안내는 `npx skills add callstack/agent-device`이지만, Claude Code 자동 모드에서는 안전 검사에 막혔습니다. 이때는 저장소를 clone한 뒤 `skills/` 아래 세 폴더를 `~/.claude/skills/`로 복사하면 됩니다.

되돌릴 때는 `claude mcp remove agent-device -s user`, `npm uninstall -g agent-device`를 실행하고 스킬 폴더 세 개를 지웁니다.

## 기본 사용 흐름

기본 흐름은 기기 준비, 앱 열기, 조작, 확인, 종료입니다. 기기는 `--platform`과 `--device`로 고릅니다.

```bash
agent-device boot --platform android --device "<에뮬레이터 이름>" --headless
agent-device install /절대/경로/app-debug.apk --platform android --device "<에뮬레이터 이름>"
agent-device open <bundle-id> --platform android --device "<에뮬레이터 이름>" --foreground
agent-device press @e5 --settle
agent-device fill @e11 "텍스트" --settle
agent-device wait text "<기대 문구>"
agent-device screenshot /절대/경로/home.png
agent-device close
```

`open`은 화면을 읽어 버튼·입력란 같은 요소마다 `@e5` 같은 참조를 붙여 돌려줍니다. `press`·`fill`에 `--settle`을 붙이면 화면이 멈출 때까지 기다린 뒤 바뀐 부분만 돌려줘서, 에이전트는 전체 화면을 다시 읽지 않고 다음 대상을 고를 수 있습니다.

여기서 자주 틀리는 점이 세 가지 있습니다.

- **참조는 화면이 바뀌면 무효가 됩니다.** 조작할 때마다 돌아온 차이에서 새 참조를 고릅니다.
- **스크린샷은 확인이 아닙니다.** 결과는 `wait text`나 `wait <selector>`로 확인하고, 스크린샷은 증거로만 남깁니다.
- **`install`에는 절대 경로를 줍니다.** 상대 경로는 agent-device 데몬의 작업 폴더 기준으로 풀려서 "App binary not found"가 납니다.

Flutter 앱 기준으로, 설치할 앱은 iOS 시뮬레이터용은 `flutter build ios --simulator --debug`, Android용은 `flutter build apk --debug`로 빌드합니다.

## Flutter에서 주의할 점

agent-device는 화면을 접근성 트리로 읽습니다. 그래서 Flutter에서는 글자가 있는 위젯만 기본으로 잡히고, 아이콘 버튼이나 컨테이너는 보이지 않습니다. 이런 위젯에는 `Semantics(identifier:)`나 `semanticLabel`을 붙여야 selector로 찾을 수 있습니다. Flutter의 `Key`는 접근성 트리에 나오지 않습니다.

접근성 트리의 라벨은 단말기의 언어 설정을 따라갑니다. 같은 앱이라도 언어가 영어로 설정된 단말기에서는 영어 라벨, 한국어로 설정된 단말기에서는 한국어 라벨로 읽힙니다. 글자로 찾으면 단말기 언어 설정에 따라 selector가 달라지므로, `identifier`로 찾는 편이 안정적입니다.

iOS에서는 AdMob 테스트 배너가 `platform_view`, `webview`, `link` 노드로 함께 잡힙니다. 리플레이 스크립트의 selector는 이 노드를 피해서 씁니다.

## 참고

- agent-device 저장소: <https://github.com/callstack/agent-device>
- agent-device 에이전트 설정 문서: <https://oss.callstack.com/agent-device/docs/agent-setup>
- Google Artemis: <https://github.com/google/artemis>
- Maestro Flutter 지원 문서: <https://docs.maestro.dev/platform-support/flutter>
