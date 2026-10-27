---
layout: post
title: "agent-device로 테스트 자동화 (2)"
description: "iPhone 러너 서명(자동·수동)과 Android 무선 디버깅으로 agent-device를 실기기에 붙이는 방법과 함정."
date: 2026-10-27
category: ai-agent
tags: [claude, agent-device, flutter, qa]
---

agent-device는 시뮬레이터·에뮬레이터와 같은 명령으로 실기기도 다룹니다. 다만 iPhone 실기기는 화면을 조작할 테스트용 앱을 서명해서 기기에 설치해야 하고, Android 실기기는 연결 방식에 따라 기기를 따로 지정해야 합니다. 이 글은 실기기가 필요한 이유, iPhone·Android 실기기를 연결하는 준비, 실기기에서 앱을 다룰 때의 주의점을 정리합니다. 기준 버전은 agent-device 0.21.31(2026-10-24)입니다.

설치와 기본 사용 흐름은 [1편]({{ "/2026/10/25/agent-device-test-automation-1.html" | relative_url }})에 있습니다.

## 왜 실기기가 필요했나

시뮬레이터와 에뮬레이터는 앱 화면을 확인하기엔 충분하지만, 스토어에 배포한 빌드가 실제 사용자 기기에서 어떻게 동작하는지는 재현하지 못합니다. 실기기로 확인해야 했던 것은 세 가지였습니다.

**스토어 빌드의 업데이트와 재설치.** TestFlight로 받은 빌드를 기존 App Store판 위에 덮어 설치하는 업데이트 경로, 앱을 지우고 다시 깐 뒤 백업을 복원하는 경로는 실기기에서만 확인할 수 있습니다. 백업 파일이 덮이지 않았는지도 기기의 Files 앱에서 iCloud Drive를 열어, 설치 전후의 파일 크기와 수정 시각으로 비교했습니다.

**첫 실행 때 뜨는 시스템 창.** 앱 추적 허용(ATT) 같은 시스템 창이 앱 화면과 어떤 순서로 뜨는지는 실제 설치 상태에서 봐야 합니다. 재설치하면 이런 동의 이력도 함께 초기화되므로, 확인하려는 상태를 기기에서 만들 수 있는지부터 따져 봐야 합니다.

**실제 광고.** Google 광고 SDK는 에뮬레이터를 자동으로 테스트 기기로 봅니다. logcat에 `This request is sent from a test device.`가 찍히고, 운영 광고 ID를 쓴 release 빌드에서도 테스트 광고만 나옵니다. 그래서 광고를 못 받는 경우(no-fill, 광고 서버가 보여 줄 광고를 찾지 못한 상태)도 에뮬레이터로는 재현되지 않습니다. 테스트 기기로 등록하지 않은 실기기에서는 logcat에 `setTestDeviceIds` 안내가 찍히고 실제 광고가 요청됩니다. 이때 광고는 누르지 않고(무효 클릭), 운영 광고를 끝까지 보는 것은 세션당 한 번으로 제한하며, 나머지는 logcat의 광고 로드 결과로 판단합니다.

## iPhone 실기기 준비

iPhone 실기기에서는 agent-device가 XCTest 러너를 기기에 설치합니다. XCTest 러너는 화면을 읽고 대신 눌러 주는 테스트용 앱이고, 개발용 인증서로 서명해야 설치됩니다. 첫 실행은 러너를 빌드하느라 오래 걸리고, 그동안 케이블 연결을 유지해야 합니다.

**자동 서명.** agent-device 문서 기준으로, Xcode에 Apple 개발자 계정이 로그인돼 있으면 팀 ID만 주면 됩니다. 러너의 번들 ID를 바꾸려면 `AGENT_DEVICE_IOS_BUNDLE_ID`도 함께 줍니다.

```bash
export AGENT_DEVICE_IOS_TEAM_ID=<팀 ID>
```

**수동 서명.** Xcode에 계정이 없거나 기존 개발 프로파일이 Xcode 관리형이면 자동 서명을 쓸 수 없습니다. 이때는 App Store Connect API 키로 러너용 개발 프로파일을 직접 만듭니다. fastlane의 `sigh`를 쓰면 와일드카드 앱 ID(`*`)로 등록된 기기를 담은 프로파일이 만들어집니다.

```bash
# key.json — key_id, issuer_id, key(.p8 파일 내용), in_house: false
fastlane sigh --development --app_identifier "*" --team_id <팀 ID> \
  --api_key_path key.json --provisioning_name "<프로파일 이름>" \
  --output_path <폴더> --skip_install --skip_certificate_verification
```

`key.json`에 .p8 파일 경로(`key_filepath`)를 넣었을 때는 실패했고, 파일 내용을 `key`에 넣자 만들어졌습니다. 만든 프로파일은 `~/Library/MobileDevice/Provisioning Profiles/<UUID>.mobileprovision`으로 복사합니다. 키 파일은 쓰고 나면 지웁니다.

그다음 서명 정보 세 개를 환경변수로 줍니다. 서명 인증서는 `security find-identity -v -p codesigning`이 보여 주는 SHA-1 값이고, 프로파일은 `sigh`에서 정한 이름으로 지정했습니다.

```bash
export AGENT_DEVICE_IOS_TEAM_ID=<팀 ID>
export AGENT_DEVICE_IOS_SIGNING_IDENTITY=<인증서 SHA-1>
export AGENT_DEVICE_IOS_PROVISIONING_PROFILE="<프로파일 이름>"
export AGENT_DEVICE_STATE_DIR=<별도 상태 폴더>
```

`AGENT_DEVICE_STATE_DIR`은 agent-device 데몬의 상태 폴더입니다. 다른 작업이 쓰는 기본 데몬과 분리하려고 상태 폴더를 따로 지정했습니다. 이 변수들과 작업 폴더(`cd`)를 래퍼 스크립트 하나에 묶어 두면 명령마다 같은 환경으로 실행됩니다.

**Mac과 기기 설정.** 서명 외에 세 가지가 맞아야 러너가 동작합니다.

1. Mac의 개발자 도구 보안이 켜져 있어야 합니다. 꺼져 있으면 러너가 `Developer mode is disabled for Apple development tools`에서 멈춥니다. 기기의 개발자 모드와는 다른 Mac 쪽 설정이고, 관리자 권한으로 `sudo DevToolsSecurity -enable`을 실행합니다.
2. iPhone 설정 → 개발자 → 'UI 자동화 활성화'가 켜져 있어야 합니다. 꺼져 있으면 러너가 설치되고 테스트가 시작된 뒤에도 응답이 없습니다.
3. 화면을 켜고 잠금을 풀어 둡니다. 러너가 'Starting XCTest runner'에서 시간 초과된 시점에 기기는 잠겨 있었습니다. 잠금을 풀고 다시 시도하지는 못해서 원인은 정황까지만 확인했지만, 시작 전에 `xcrun devicectl device info lockState --device <UDID>`로 잠금 상태를 보는 편이 안전합니다.

## iPhone에서 앱 다루기

실기기의 앱 설치 목록 확인과 삭제는 Xcode의 `devicectl`로 합니다.

```bash
xcrun devicectl list devices
xcrun devicectl device info apps --device <UDID>
xcrun devicectl device uninstall app --device <UDID> <bundle-id>
```

러너도 같은 방법으로 지웁니다. 러너의 번들 ID는 `com.callstack.agentdevice.runner.uitests.xctrunner`이고, 지운 뒤 `open`을 하면 러너를 다시 빌드·설치합니다.

TestFlight로 테스트 빌드를 설치할 때, 같은 앱의 App Store판이 이미 깔려 있으면 "You may lose the app's data."라는 경고가 뜹니다. 이 경고의 Install이 덮어쓰기입니다. 에이전트는 이 경고에서 멈추고 사람에게 묻도록 하는 편이 안전합니다.

앱을 지우면 기기 안 데이터가 사라집니다. 백업이 있는 앱이라면 지우기 전에 앱 설정의 백업이 켜져 있고 마지막 백업 시각이 방금인지 스크린샷으로 남기고, 아니면 지우지 않고 멈추게 합니다.

화면 조작에서 하나 더 있습니다. 설정 화면의 스위치는 ref로 누르면 행 가운데를 눌러 켜지지 않는 경우가 있습니다. 이때는 `snapshot --json`이 주는 요소 좌표(rect)로 스위치의 오른쪽 끝을 좌표로 누릅니다.

## Android 실기기 연결

USB 디버깅으로 연결한 Android 실기기는 에뮬레이터와 똑같이 다룹니다. 무선 디버깅은 연결 직후 `adb devices`에 보이지 않을 수 있습니다. `adb mdns services`에 `_adb-tls-connect` 서비스가 뜬 뒤에야 잡히므로, 바로 비어 있다고 판단하지 말고 몇 초 뒤 다시 확인합니다.

무선 연결의 serial은 긴 mDNS 이름이라 에뮬레이터와 섞이기 쉽습니다. 모든 `adb`·`agent-device` 명령에 `--serial`을 붙입니다. agent-device 세션은 작업 폴더마다 만들어지므로, 같은 폴더에서 에뮬레이터를 쓰던 중이면 "already bound to android device" 오류가 납니다. 이때는 `--session <이름>`으로 세션을 따로 엽니다.

```bash
adb mdns services
agent-device open <bundle-id> --platform android --serial <serial> --session <이름> --foreground
agent-device close --session <이름>
adb disconnect <serial>
```

Android에서 자주 틀리는 점은 세 가지입니다.

- **adb 셸 명령은 한 문자열로 인용합니다.** `adb shell "cmd notification post -t '제목' <tag> '본문'"`처럼 전체를 묶지 않으면 adb가 공백에서 인자를 쪼갭니다.
- **키보드가 버튼을 가리면 잡히지 않습니다.** `adb shell input keyevent KEYCODE_BACK`으로 키보드를 닫고 다시 snapshot합니다.
- **공백이 든 selector는 따옴표로 감쌉니다.** `label="..."` 형태로 쓰고, 플래그를 변수 한 덩어리로 넘기면 "Unknown flag"가 납니다.

전면 광고처럼 앱이 아닌 화면이 위에 떠 있으면, 스냅샷만으로는 앱이 어떤 상태인지 판단하기 어렵습니다. 이때는 adb로 시스템 상태를 함께 확인합니다.

```bash
adb -s <serial> shell dumpsys activity activities | grep topResumedActivity   # 지금 맨 앞의 화면
adb -s <serial> shell pidof <패키지>                                          # 앱 프로세스가 살아 있는지
adb -s <serial> logcat -d | grep -E "FATAL|AndroidRuntime"                     # 앱이 죽은 흔적
```

맨 앞 화면이 광고 화면인지 앱인지, 앱이 뒤에서 살아 있는지, 죽었다면 그 기록이 남았는지를 스냅샷과 맞춰 봅니다. 광고 화면은 접근성 트리에 `webview`·`link` 노드가 많이 잡히므로, 스냅샷을 볼 때 이 노드는 걸러서 봅니다.

## 참고

- agent-device 저장소: <https://github.com/callstack/agent-device>
- agent-device 에이전트 설정 문서: <https://oss.callstack.com/agent-device/docs/agent-setup>
- fastlane sigh 문서: <https://docs.fastlane.tools/actions/sigh/>
- Android 무선 디버깅: <https://developer.android.com/tools/adb#wireless>
