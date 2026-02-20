# Jira Webhook 기반 QA 알림 자동화 구축



## 프로젝트 개요

QA 진행 중 Jira 이슈 상태 변경을 수동으로 확인해야 하는 비효율을 개선하기 위해,
 **Webhook 기반 실시간 알림 시스템을 통해 Synology Chat으로 자동 전달되는 구조의 알림 정책을 설계하고 연동 테스트 및 검증을 수행한 프로젝트입니다.**

이를 통해 QA와 개발 간 이슈 대응 속도를 개선하고 협업 효율을 향상시켰습니다.

------



## 추진 배경

기존 QA 프로세스에서는 다음과 같은 문제점 발생했습니다.

- Jira 이슈 상태 변경을 수동으로 확인해야 하는 구조
- 이슈 상태 변경 인지 지연으로 인한 대응 속도 저하
- 개발 완료 후 QA 재확인까지 대기 시간 발생
- Jira와 메신저 간 정보 연동 부재

→ 이슈 상태 변경을 실시간으로 공유할 수 있는 자동화된 알림 체계 필요



------

## 시스템 구성

전체 구조는 아래와 같습니다.



Jira (Groovy 기반 Webhook)
   ↓
NAS Server (Node.js Webhook Listener)
   ↓
Synology Chat (Webhook 메시지 수신)



### 구성 요소 역할

| 구성                  | 역할                                       |
| --------------------- | ------------------------------------------ |
| Jira                  | 이슈 생성, 상태 변경 이벤트 발생           |
| Groovy (ScriptRunner) | 이벤트 발생 시 Webhook 호출 및 데이터 전달 |
| NAS Server (Node.js)  | Webhook 수신 및 Synology Chat으로 전달     |
| Synology Chat         | 최종 알림 메시지 수신 및 사용자 표시       |

------



## 주요 기능

- 이슈 생성 시 자동 알림
- 상태 변경 시 담당자 알림
- 코멘트 등록 시 알림
- Jira 이슈 바로가기 링크 제공

------



## 담당 역할

- Jira Webhook 기반 알림 정책 설계
- 알림 메시지 템플릿 구조 정의
- Webhook 연동 시나리오 정의
- 개발자 구현 이후 Webhook 연동 테스트 및 검증 수행
- 실제 QA 업무 적용 및 활용

※ Webhook Listener(Node.js) 구현은 개발자가 담당하였으며,
 저는 QA 담당자로서 연동 구조 설계 참여 및 테스트 검증을 수행했습니다.

------



## 테스트 및 검증

다음 항목을 중심으로 검증을 진행했습니다.

- Jira 이벤트 발생 시 Webhook 정상 전달 여부 확인
- Synology Chat 메시지 정상 수신 확인
- 알림 메시지 내용 정확성 확인
- Jira 이슈 링크 정상 이동 확인 (PC / Mobile)

------



## 적용 효과

- Jira 상태 변경 즉시 확인 가능
- QA 대응 속도 개선
- 이슈 공유 프로세스 개선
- QA 업무 효율성 향상

------



## 문서

상세 내용은 아래 문서를 참고해주세요.

- [jira]: https://github.com/Kwon-Giil/QA/blob/master/Jira/jira-webhook/jira%20%EC%9B%B9%ED%9B%85%20%EB%A9%94%EC%8B%9C%EC%A7%80%20%EB%A9%98%ED%8A%B8%20%EC%B4%88%EC%95%88.txt	"jira 웹훅 메시지 초안"

  

- [Jira]: https://github.com/Kwon-Giil/QA/blob/master/Jira/jira-webhook/Jira%20%EC%9B%B9%ED%9B%85%20%EC%95%8C%EB%A6%BC%20%EC%84%9C%EB%B9%84%EC%8A%A4%20%EA%B2%B0%EA%B3%BC%20%EB%B3%B4%EA%B3%A0%EC%84%9C.pdf	"Jira 웹훅 알림 서비스 결과 보고"

  

------



## 구현 결과

### 알림 메시지 예시

(

[지라]: https://github.com/Kwon-Giil/QA/blob/master/Jira/jira-webhook/%EC%A7%80%EB%9D%BC%20%EC%9B%B9%ED%9B%85%20%EA%B2%B0%EA%B3%BC%EB%AC%BC.png	"지라 웹훅 결과물"

 참고)

------

## 기술 환경

- Jira
- Groovy (ScriptRunner)
- Node.js (Webhook Listener)
- Synology Chat
- Webhook

------



## 프로젝트 의의

- Webhook 기반 시스템 구조 이해
- QA 관점에서의 업무 자동화 경험
- 개발자와의 협업을 통한 시스템 연동 경험



