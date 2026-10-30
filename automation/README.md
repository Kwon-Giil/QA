# MoneyMove 웹 자동화 프로젝트

## 1. 프로젝트 소개

머니무브 웹 페이지의 주요 사용자 흐름을 대상으로 E2E(End-to-End) 테스트 자동화를 구현한 프로젝트

Python과 Playwright를 활용해 로그인부터 투자 신청 및 신청 취소까지의 과정을 자동화하고, Docker와 GitHub Actions를 연동해 테스트 실행 환경 및 CI 자동화 구성 경험 확보 목적

GitHub-hosted Runner에서 발생한 외부 서비스 접근 문제를 해결하기 위해 로컬 PC에 Self-hosted Runner를 구성하고, 해당 환경에서 GitHub Actions 워크플로우가 실행되도록 설정

## 2. 개발 환경 및 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python |
| IDE | Visual Studio Code |
| Test Automation | Playwright |
| Container | Docker |
| CI | GitHub Actions |
| Runner | GitHub Actions Self-hosted Runner |
| AI Assistant | Gemini |
| Version Control | Git / GitHub |

## 3. 테스트 대상 및 범위

**테스트 대상:** 머니무브 웹 페이지 (https://moneymove.ai)

**주요 테스트 시나리오**

1. 로그인
2. 투자 신청
3. 투자 신청 취소

사용자의 주요 서비스 이용 흐름을 하나의 시나리오로 연결해 각 단계가 정상적으로 수행되는지 확인하도록 구성

별도의 본인 인증 과정 등이 필요하지 않은 사용자 시나리오 위주로 구성

## 4. 프로젝트 구성

| 구성 요소 | 역할 |
|---|---|
| Python / Playwright 테스트 코드 | 웹 페이지의 사용자 동작 및 주요 시나리오 자동화 |
| Docker 관련 설정 | 테스트 실행 환경 구성 및 빌드 |
| GitHub Actions Workflow | 테스트 자동화 작업 정의 및 실행 |
| `.env` | 로컬 테스트 실행에 필요한 환경변수 관리 |
| GitHub Repository Secrets | GitHub Actions 실행 시 필요한 인증정보 관리 |
| Self-hosted Runner | 로컬 PC에서 GitHub Actions 작업 실행 |

## 5. 실행 방법

### 사전 준비

- Python
- Docker
- Playwright 및 프로젝트 의존성
- 테스트 실행에 필요한 환경변수

### 환경변수 설정

로컬 실행 시 `.env` 파일에 필요한 환경변수 설정.

GitHub Actions에서 실행할 경우에는 Repository Secrets에 동일한 환경변수 이름으로 인증정보 등록.

로컬 환경과 CI 환경에서 동일한 변수명을 사용하도록 관리.

### 테스트 실행

프로젝트 의존성을 설치한 뒤 Playwright 테스트 실행.

※ 구체적인 설치 및 실행 명령어는 저장소에 포함된 의존성 파일과 Workflow 설정에 맞춰 기재.

## 6. GitHub Actions CI 자동화

GitHub Actions를 이용해 테스트 자동화 워크플로우 구성

### 실행 환경 구성

초기에는 GitHub-hosted Runner의 기본 실행 환경인 `ubuntu-latest`를 사용했으나,

```yaml
runs-on: ubuntu-latest
```

이후 외부 서비스 접근 문제를 해결하기 위해 로컬 PC에 Self-hosted Runner를 등록하고 실행 환경 변경.

```yaml
runs-on: self-hosted
```

Self-hosted Runner는 로컬 PC에서 별도의 터미널을 열어 Runner 실행 프로그램을 직접 구동하는 방식으로 사용함.

Runner가 실행되어 GitHub와 연결된 상태에서 GitHub Actions 워크플로우가 작업을 전달받아 실행.

### CI 실행 흐름

1. GitHub Actions Workflow에서 테스트 작업 실행
2. 등록된 Self-hosted Runner가 작업 수신
3. 로컬 PC의 실행 환경에서 테스트 수행
4. 테스트 실행 결과 확인

Runner 실행 프로그램이 종료되어 있거나 GitHub와 연결되지 않은 상태에서는 해당 Runner가 작업을 처리할 수 없으므로, 워크플로우 실행 전에 Runner의 실행 상태를 확인해야 함.

## 7. 테스트 결과

- Playwright를 활용해 로그인부터 투자 신청 및 신청 취소까지의 E2E 시나리오 구현
- Docker를 활용한 테스트 실행 환경 구성 및 빌드 경험
- GitHub Actions를 통한 테스트 자동화 워크플로우 구성
- Self-hosted Runner를 활용해 로컬 네트워크 환경에서 CI 작업 실행 확인

## 8. 트러블슈팅

### 8-1. Docker 빌드 파일 경로 오류

**문제**

Docker 이미지 빌드 과정에서 관련 파일의 경로가 일치하지 않아 빌드가 정상적으로 진행되지 않았음.

**해결**

Docker 빌드에 필요한 파일들의 위치를 정리하고 관련 파일을 저장소 최상위 디렉터리로 이동해 경로 참조를 정비하여 해결.

**학습 내용**

Docker 빌드에서는 빌드 컨텍스트와 파일 참조 경로가 중요하다는 점을 확인함. 파일의 실제 위치뿐 아니라 Docker 빌드 명령이 기준으로 삼는 경로도 함께 고려해야 함.

### 8-2. GitHub Actions 환경변수 매핑 오류

**문제**

로컬 환경에서는 `.env` 파일을 통해 로그인이 정상적으로 수행됐지만, GitHub Actions에서는 로그인 정보를 불러오지 못했음.

확인 결과 `.env` 파일에 정의된 환경변수 이름과 GitHub Repository Secrets에 등록한 이름이 서로 일치하지 않았음.

**해결**

`.env`의 환경변수 이름과 GitHub Repository Secrets의 이름을 동일하게 맞춰 문제 해결.

**학습 내용**

로컬 환경과 CI 환경은 인증정보를 주입하는 방식이 다를 수 있으므로, 환경변수 이름과 매핑 구조를 일관되게 관리해야 함.

### 8-3. GitHub-hosted Runner의 외부 서비스 접근 문제

**문제**

GitHub-hosted Runner의 기본 환경인 `ubuntu-latest`에서 테스트를 실행했을 때 로그인 단계에서 접근 문제가 발생.

로컬 Docker 환경에서는 정상적으로 동작했지만 GitHub-hosted Runner에서는 로그인 불가.

확인 결과 GitHub-hosted Runner의 외부 IP가 Naver Cloud 측의 해외 IP 접근 제한 정책에 영향을 받는 것으로 판단.

**해결**

1. 로컬 PC를 GitHub Actions Self-hosted Runner로 등록.
2. Workflow의 실행 환경을 `ubuntu-latest`에서 `self-hosted`로 변경.
3. 별도 터미널에서 Self-hosted Runner 실행 프로그램을 직접 구동.
4. Runner가 GitHub와 연결된 상태에서 워크플로우를 실행해 테스트가 정상적으로 수행되는 것을 확인.

**학습 내용**

GitHub Actions는 워크플로우 자체뿐 아니라 실제 작업이 실행되는 Runner의 네트워크 환경에도 영향을 받음.

외부 서비스의 접근 정책으로 인해 CI 작업이 실패할 경우 테스트 코드만 확인할 것이 아니라 Runner의 IP 및 네트워크 접근 조건도 함께 점검해야 함.

또한 Self-hosted Runner는 별도로 등록하는 것만으로 작업을 처리하는 것이 아니라, Runner 실행 프로그램이 실제로 구동되어 온라인 상태를 유지해야 한다는 점을 확인함.

## 9. 학습 내용

- Playwright를 활용한 웹 E2E 테스트 자동화
- Docker 빌드 과정에서의 파일 경로 및 빌드 컨텍스트 관리
- `.env`와 GitHub Repository Secrets를 활용한 환경변수 관리
- GitHub Actions Workflow 작성 및 실행
- GitHub-hosted Runner와 Self-hosted Runner의 실행 환경 차이 이해
- CI 환경에서 발생하는 네트워크 접근 문제 분석 및 해결

Gemini를 학습 및 문제 해결 과정의 보조 도구로 활용했으며, 제안된 해결 방법은 직접 실행하고 테스트 결과를 확인하는 방식으로 검증.

## 10. 개선 및 확장

- 테스트 시나리오 확장 및 예외 상황 검증 추가
- 테스트 데이터와 인증정보 관리 방식 개선
- 실패한 테스트의 로그 및 실행 결과 수집
- 테스트 코드의 재사용성을 높이기 위한 구조 개선
- Self-hosted Runner의 자동 실행 및 운영 방식 개선
- CI 실행 결과를 기반으로 한 테스트 리포트 생성






















