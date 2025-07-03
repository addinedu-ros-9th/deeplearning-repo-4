[![표지](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%ED%91%9C%EC%A7%80.png?raw=true)](https://docs.google.com/presentation/d/1FakMHUjW8QSYNp0pCkSbHC8iK0WQIAL3S_snXaCv-xs/edit?slide=id.g369f27ec0ea_3_0#slide=id.g369f27ec0ea_3_0)
[ㄴ 클릭시 PPT 이동](https://docs.google.com/presentation/d/1FakMHUjW8QSYNp0pCkSbHC8iK0WQIAL3S_snXaCv-xs/edit?slide=id.g369f27ec0ea_3_0#slide=id.g369f27ec0ea_3_0)

![예시 이미지](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EC%98%88%EC%8B%9C%20%EC%9D%B4%EB%AF%B8%EC%A7%80.png?raw=true)
## 주제 : 무인매장 CCTV 단속 시스템 [딥러닝 프로젝트]

### 목차
**00** 팀 소개 <br/>
**01** 프로젝트 소개 <br/>
**02** 프로젝트 설계 <br/>
**03** 프로젝트 구현 <br/>
**04** 프로젝트 결과 <br/>
마무리

# 00. 팀 소개
### 팀명 : GIGACHAD
![로고](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EB%A1%9C%EA%B3%A0%E3%84%B9.png?raw=true)

언제나 우리의 마음을 바라봐주고 관리해주는 기가채드처럼 <br/>
언제나 우리 매장을 바라봐주고 관리해준다는 컨셉

### 팀원 
| 이름 | 주요 역할 |
|:---:|---|
| 김범진 (팀장) | 프로젝트 관리, 딥러닝[불꺼짐]  |
| 김채연 (팀원) | 서버 통신, 딥러닝[절도] | 
| 구민제 (팀원) | 서버, 딥러닝[파손/유기]  |
| 최원호 (팀원) | GUI 통신, 딥러닝 리팩토링  |

### 활용 기술
|분류|기술|
|---|---|
|**개발환경**|<img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=white"/> <img src="https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=Ubuntu&logoColor=white"/> <img src="https://img.shields.io/badge/VSCode-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white"/> |
|**언어**|<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white"/> <img src="https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=cplusplus&logoColor=white"/> 
|**UI**|<img src="https://img.shields.io/badge/PyQt6-28c745?style=for-the-badge&logo=PyQt6&logoColor=white"/>|
|**DBMS**| <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/>|
|**딥러닝**| <img src="https://img.shields.io/badge/YOLOv8-FFBB00?style=for-the-badge&logo=YOLO&logoColor=white" alt="YOLOv8"/> <img src="https://img.shields.io/badge/LSTM-006400?style=for-the-badge&logo=OpenAI&logoColor=white" alt="LSTM"/> <img src="https://img.shields.io/badge/ST--GCN-1E90FF?style=for-the-badge&logo=GraphQL&logoColor=white" alt="ST-GCN"/>|
|**협업**|<img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white"/> <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white"/> <img src="https://img.shields.io/badge/SLACK-4A154B?style=for-the-badge&logo=slack&logoColor=white"/> <img src="https://img.shields.io/badge/Confluence-172B4D?style=for-the-badge&logo=confluence&logoColor=white"/> <img src="https://img.shields.io/badge/JIRA-0052CC?style=for-the-badge&logo=jira&logoColor=white"/> |

### 일정관리
![일정](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EC%9D%BC%EC%A0%95.png?raw=true)

**25.5.27 ~ 25.7.1 약 5주간 진행** <br/>
**Sprint1** : 기능정의 및 기술조사 <br/>
**Sprint2** : 기술조사 및 설계 <br/>
**Sprint3** : 기술 및 설계 검토 <br/>
**Sprint4** : 구현 및 1차 연동테스트 <br/>
**Sprint5** : 구현 및 2차 연동테스트 <br/>
**Sprint6** : 전체 연동테스트 

# 01. 프로젝트 소개
### 주제 선정 배경
![주제 선정 배경1](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EC%A3%BC%EC%A0%9C%20%EC%84%A0%EC%A0%95%20%EB%B0%B0%EA%B2%BD1.png?raw=true)

무인매장 CCTV를 주제로 선정한 이유 <br/>
- 매장 내 감시인력의 부재 <br/>
- 심야 취약 시간대 <br/>
- 즉각적 대응이 어려움 <br/>
  
위의 이유로 **무인매장 대상으로 범죄**가 증가하고 있는 추세입니다.

그렇기에 무인매장을 관리해주는 시스템의 수요가 늘어나 이를 주제로 선정하였습니다.

### 사용자 요구사항 (User Requirements)
| 번호 | 설명 |
|------|----------------|
| 1 | 불법행위가 감지되면 관리자에게 알람을 한다. <br/> 불법행위는 ‘파손’, ‘유기’, ‘절도’, ‘시설물 제어’가 있다.|
| 2 | 불법행위 감지 시 해당 영상을 저장하고 이후에 검색 가능해야 한다. |
| 3 | 불법행위 한 사람을 구분해서 블랙리스트를 만든다. |
| 4 | 관리자가 매장을 실시간으로 CCTV를 모니터링 한다. |
| 5 | 매장에 한달에 얼마나 고객이 방문했는지, 체류시간이 어느정도 되는지 파악할 수 있다. |
| 6 | 고객의 동선을 파악해서 최적의 상품 배치를 추천해준다. |
| 7 | 단골 손님과 일반 손님을 구분 할 수 있다. |

[ **요약** ] <br/>
![사용자 요구사항](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EC%82%AC%EC%9A%A9%EC%9E%90%20%EC%9A%94%EA%B5%AC%EC%82%AC%ED%95%AD.png?raw=true)

사용자 요구사항을 크게 3가지로 요약하면, <br/>
'불법 감지 / 통계 / 기록/' 이렇게 3가지로 요약할 수 있습니다.

# 02. 프로젝트 설계
## System Requirements
| SR_ID | Category | Name | Description | Priority |
|-------|----------|------|-------------|----------|
| SR_01 | 불법행위 감지 | 불법행위 감지 기능 | CCTV의 영상으로 파손, 유기, 절도, 전등 끄기 에 대한 불법행위를 감지한다. <br/> - 파손 - 과격한 행위 / 물건을 던지는 행위 / 키오스크를 부수는 행위 <br/> - 유기 - 객체를 바닥에 두는 행위 / 책상 및 선반에 올려놓는 행위유기 - 객체를 바닥에 두는 행위 / 책상 및 선반에 올려놓는 행위 <br/> - 절도 - 가방에 넣는 행위 / 주머니에 넣는 행위 <br/> - 전등 - Off | R |
| SR_02 | 불법행위 감지 | 불법행위 감지 알람 기능  | 불법행위 감지시 사용자의 GUI에 알린다. <br/> - TTS 음성 <br/> - 팝업창 <br/> - 작업표시줄 시스템 트레이 | R |
| SR_03 | 불법행위 감지 | 불법행위 영상 자동저장 기능 | 불법행위가 발생하면 해당 영상을 자동으로 저장 할 수 있다. | R |
| SR_04 | 불법행위 감지 | 불법행위 영상 조회 기능 | 사용자는 자동으로 저장된 불법행위 영상을 조회 할 수 있다. | R |
| SR_05 | 불법행위 감지 | 불법행위 데이터 생성 기능 | 불법행위 감지 시 통계 데이터를 생성한다. <br/> - 매장 ID (store_id): 불법행위가 발생한 매장 고유 ID <br/> - 행위 유형 (action_type): 절도, 파손, 유기, 흡연 등 <br/> - 발생 시간 (timestamp): 불법행위 발생 시각 (YYYY-MM-DD HH:MM:SS) <br/> - 발생 일자 (date): 날짜 기준 통계용 필드 (YYYY-MM-DD) <br/> - 시간대 (hour): 시간대별 통계 (0~23시) <br/> - 행위자 ID (optional): 불법행위자의 추정 ID (선택, 얼굴매칭/트래킹 기반) <br/> - 감지 소스 (source): 어떤 CCTV에서 감지되었는지 (카메라 위치) <br/> - 증거 영상 경로 (video_url): 감지 당시의 영상 경로 <br/> - AI 감지 신뢰도 (confidence): AI 감지 모델의 confidence score (선택) | R |
| SR_06 | 실시간 관제 | CCTV 실시간 모니터링 기능 | 사용자는 매장의 CCTV를 실시간으로 확인할 수 있다. | O |
| SR_07 | 고객 행동 분석 | 동선 기반 상품 추천 기능 | 고객의 이동 동선을 분석하여 최적의 상품 배치 위치를 추천해준다. | O |
| SR_08 | 고객 행동 분석 | 고객 방문 및 체류 분석 및 데이터 생성 기능 | 고객 방문 횟수와 체류 시간을 분석하여 통계 데이터를 생성한다. <br/> - 매장 ID (store_id): 고객이 방문한 매장 고유 ID<br/> - 고객 ID (customer_id): 방문한 고객의 고유 ID (익명 ID 또는 MAC 주소 기반 비식별 ID 가능) <br/> - 입장 시각 (entry_time): 고객이 매장에 들어온 시간 (YYYY-MM-DD HH:MM:SS)  <br/> - 퇴장 시각 (exit_time): 고객이 매장에서 나간 시간 (YYYY-MM-DD HH:MM:SS) <br/> - 체류 시간 (stay_duration): 고객의 총 체류 시간 (초 또는 분 단위, exit_time - entry_time 계산) <br/> - 방문 일자 (visit_date): YYYY-MM-DD 형식의 방문 일자 (통계 집계용) <br/> - 방문 시간대 (visit_hour): 고객이 방문한 시각의 시간대 (0~23) | O |
| SR_09 | 불법행위자 관리 | 블랙리스트 등록 기능 | 불법행위를 한 사람을 블랙리스트로 등록한다. | O |
| SR_10 | 통계 시각화/조회 | 데이터 통계 조회 기능 | 사용자는 고객 방문 횟수, 평균 체류 시간 통계를 일별/월별로 조회할 수 있다. <br/> 통계 데이터를 그래프(선형, 막대, 파이 차트) 형태로 시각화하여 사용자에게 보여준다. | O |
| SR_11 | 통계 시각화/조회 | 불법행위 통계 조회 기능 | 사용자는 매장에서 발생한 불법행위의 유형별 / 건수별 통계를 볼 수 있다. <br/> 특정 날짜 또는 시간대에 발생한 불법행위 건수를 조회 할 수 있다. <br/> 전체 불법행위 유형(절도, 파손, 유기)별 비율을 시각화 된 형태로 조회 할 수 있다. | R |

![System Requirements](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/system%20requirements.png?raw=true)

기능 리스트를 요약하면 크게 3가지로 나눌 수 있습니다. <br/>
불법행위 감지 기능 / 통계 시각확 기능 / 기록 및 클립 조회 기능 

### 서비스 흐름
![서비스 흐름](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EC%84%9C%EB%B9%84%EC%8A%A4%20%ED%9D%90%EB%A6%84.png?raw=true)

### System Architecture
![System Architecture](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/system%20architecture.png?raw=true)

### 시퀀스 다이어그램

<details>
<summary>SC-01 : 불법행위 감지 및 관리자 알림 및 영상 자동저장 [클릭] </summary>

![SC-01](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/SC-01.png?raw=true)

</details>

<details>
<summary> SC-02 : 불법행위 영상 검토 및 다시보기 [클릭] </summary>

![SC-02](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/SC-02.png?raw=true)

</details>

<details>
<summary> SC-03 : CCTV 실시간 모니터링 [클릭] </summary>

![SC-03](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/SC-03.png?raw=true)

</details>

<details>
<summary> SC-04 : 불법행위 통계 데이터 생성 및 조회 [클릭] </summary>

![SC-04](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/SC-04.png?raw=true)

</details>

### ERD
![ERD](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/erd.png?raw=true)

### Interface Specification
#### status code 
| 요청 결과                           | 코드 |
|-------------------------------------|------|
| 정상 요청, 데이터 응답 성공         | 200  |
| 정상 요청, 정보없음 or 응답 실패    | 401  |
| 잘못된 요청                        | 404  |
| 서버 내부 오류                     | 500  |

#### 중앙서버 ↔︎ GUI

| Interface ID | Function                | Method | Endpoint                  | Sender      | Receiver    | Request Data Example                                                                                                   | Response Data Example / Description                                                                                      |
|--------------|------------------------|--------|---------------------------|-------------|-------------|------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| IF-01        | 로그인                  | POST   | /auth/login               | GUI         | 중앙서버    | `{"user_id": "user01", "passwd": "user01"}`                                                                            | status_code - 아이디 오류 401, 비밀번호 오류 402                                                                          |
| IF-02        | 사용자 개인정보         | POST   | /load/private_information | GUI         | 중앙서버    | `{"user_id": "user01"}`                                                                                                | `{"name":"최기가", "email":"user01@gmail.com", "store_name" : "GS25 금천점"}`                                             |
| IF-03        | notification           | POST   | /load/notification        | GUI         | 중앙서버    | `{"user_id": "user01"}`                                                                                                | `[{"event_type": "broken", "time": "...", "video_url": "..."} ...]`<br>24시간 기준 불법행위 알림 데이터 송신               |
| IF-04        | 영상 실행               | GET    | /load/video               | GUI         | 중앙서버    | `{"user_id": "user01", "video_url": "video_42.mp4"}`                                                                   | `{ "content_type": "video/mp4", "streaming": true }`<br>HTTP 응답 본문에 MP4 파일의 바이너리 데이터를 포함해 직접 전송     |
| IF-05        | detect log 조회         | POST   | /load/detect_log/filter   | GUI         | 중앙서버    | `{ "user_id": "user01", "period": "today", "start_date": "...", "end_date": "...", "event_type": [...], "is_checked": [0,1], "favorite": [0,1] }` | `[{"store_name": "...", "time": "...", "event_type": "...", ...}]`<br>조건 조합에 따라 전체/기간별/필터링 데이터 반환      |
| IF-06        | 불법행위 종류 변경      | POST   | /change/event_type        | GUI         | 중앙서버    | `{ "user_id": "user01", "store_name": "GS 금천점", "timestamp": "...", "event_type": "theft" }`                        | status_code<br>DB에서 event_type, confidence=1로 update                                                                  |
| IF-07        | 불법 확정               | POST   | /change/is_checked        | GUI         | 중앙서버    | `{ "user_id": "user01", "store_name": "GS 금천점", "timestamp": "..." }`                                               | status_code<br>DB에서 is_checked, confidence=1로 update                                                                  |
| IF-08        | 영상 삭제               | POST   | /delete/video             | GUI         | 중앙서버    | `{ "user_id": "user01", "video_url": "video_42.mp4" }`                                                                 | status_code<br>DB에서 해당 영상 delete                                                                                   |
| IF-09        | 통계 조회               | POST   | /load/dashboard           | GUI         | 중앙서버    | `{ "user_id": "user01", "date": "YYYY-MM" }`                                                                           | `{ "event_types": [...], "monthly_stats": [ ... ] }`<br>파손, 유기, 절도, 전등 끔 순                                     |
| IF-10        | 영상 선택 삭제          | POST   | /delete/checked_video     | GUI         | 중앙서버    | `{ "user_id": "user01", "video_urls": ["video_42.mp4", "video_43.mp4"] }`                                              | `{ "status_code": 200 }`<br>여러 영상 삭제                                                                               |
| IF-11        | 영상 즐겨찾기 기능      | POST   | /favorite/video           | GUI         | 중앙서버    | `{ "user_id": "user01", "video_url": "video_42.mp4", "favorite": 1 }`                                                  | `{ "status_code": 200 }`<br>favorite 1: 추가, 0: 삭제                                                                    |

# 03. 프로젝트 구현
## 딥러닝
### 데이터 전처리
![데이터 전처리1](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EB%8D%B0%EC%9D%B4%ED%84%B0%20%EC%A0%84%EC%B2%98%EB%A6%AC1.png?raw=true)

![데이터 전처리2](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EB%8D%B0%EC%9D%B4%ED%84%B0%20%EC%A0%84%EC%B2%98%EB%A6%AC2.png?raw=true)

![데이터 전처리3](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EB%8D%B0%EC%9D%B4%ED%84%B0%20%EC%A0%84%EC%B2%98%EB%A6%AC3.png?raw=true)

데이터 전처리 과정은 
- 영상 촬영 (행위 별로 100개씩 총 400개 영상)
- 영상 컷 편집 (불법 행위 장면만 남기기)
- 관절점 추출 및 정규화 및 시퀀스 구성

순으로 진행되었습니다.

### 딥러닝 모델 선발 과정
![딥러닝 모델 선발 과정](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EB%AA%A8%EB%8D%B8%20%EC%84%A0%EB%B0%9C%EA%B3%BC%EC%A0%951.png?raw=true)
YOLO BBox 추출 + CNN 모델은 한 프레임을 판단하는 경우에는 우수했으나, 연속된 프레임을 보고 해당 행위를 검출하는 것에는 부족했습니다.
YOLO Pose + LSTM 모델은 꽤 높은 성능을 보여주었으나, 단순한 모델 구조와 공간적 특징을 반영하지 못해 복잡한 동작을 인식할 수 없었습니다.
YOLO Pose + ST-GCN 모델은 이러한 LSTM 모델의 단점을 조금이나마 개선한 모델로, 최종적으로 선정하게 되었습니다.

![딥러닝 모델 선발 과정2](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EB%AA%A8%EB%8D%B8%20%EC%84%A0%EB%B0%9C%EA%B3%BC%EC%A0%952.png?raw=true)

- L2A : AI 허브만 + LSTM 2레이어
- L2BA : AI 허브만 + LSTM 2레이어 베스트 모델(파라미터 개선)
- L2P : 실 데이터 전이학습 + LSTM 2 레이어 + 시퀀스 데이터 패딩 적용
- L2PL : 실 데이터 전이학습 + LSTM 2 레이어 + 시퀀스 이하 길이 데이터 제거
- L3 : 실 데이터 전이학습 + LSTM 3 레이어
- L3DU : 실 학습 데이터 일부 변경 후 전이학습 + LSTM 3 레이어
- SG : L3DU 모델과 같은 데이터에 + ST-GCN
- SGB : SG 베스트 모델(파라미터 개선)
- SGQ : SGB를 양자화한 모델

LSTM 모델도 개선을 통해 많이 좋아졌으나, ST-GCN은 전반적으로 모두 높은 정확도를 보여주는 것을 알 수 있습니다.

![딥러닝 모델 구조1](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EB%AA%A8%EB%8D%B8%20%EA%B5%AC%EC%A1%B01.png?raw=true)

ST-GCN은 단순히 관절의 X, Y 좌표 뿐만 아니라 인접 행렬 정보를 함께 입력값으로 넣어주어 특징 추출에 활용합니다.

![딥러닝 모델 구조2](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EB%94%A5%EB%9F%AC%EB%8B%9D%20%EB%AA%A8%EB%8D%B8%EA%B5%AC%EC%A1%B02.png?raw=true)

인접 행렬 A에서 이웃된 노드의 정보를 함께 넣어줌에 따라 시간적 변화 뿐만 아니라 공간적 변화를 반영합니다.

![딥러닝 학습 결과](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EB%94%A5%EB%9F%AC%EB%8B%9D%20%ED%95%99%EC%8A%B5%20%EA%B2%B0%EA%B3%BC.png?raw=true)

Theft 라벨에서 비교적 낮은 성능을 보이는 이유는 Theft 행위의 시간이 다른 행위에 비해 짧고, 다양한 패턴으로 일어나기 때문입니다. 학습 데이터를 추가하거나, 데이터 증강 기법을 통해 성능 개선을 기대할 수 있습니다.

### GUI
GUI 파일 구조

![gui 파일 구조](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/gui%20%EA%B5%AC%EC%A1%B0.png?raw=true)

진입점 : main.py <br/>
화면 전환 : main을 통해 login.py <-> layout.py <br/>
layout 의 컴포넌트 : cctv / dashboard / detect_log <br/>
팝업 : video_popup <br/>
스타일 : style.py 에서 모든 qss파일 임포트해옴 <br/>

#### 화면 구성도 : 로그인
![화면 구성도 로그인](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EB%A1%9C%EA%B7%B8%EC%9D%B8%20%ED%99%94%EB%A9%B4.png?raw=true)

#### 화면 구성도 : CCTV
![화면 구성도 CCTV](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/cctv%20%ED%99%94%EB%A9%B4.png?raw=true)

#### 화면 구성도 : Dashboard
![화면 구성도 Dashboard](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/dashboard%20%ED%99%94%EB%A9%B4.png?raw=true)

#### 화면 구성도 : Detect Log
![화면 구성도 Detect Log](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/detect%20log%20%ED%99%94%EB%A9%B4.png?raw=true)

# 04. 프로젝트 결과
### 로그인 기능
![로그인 기능](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EB%A1%9C%EA%B7%B8%EC%9D%B8%20%EA%B8%B0%EB%8A%A5.gif?raw=true)

### CCTV : 불법행위 감지 기능 (유기)
![불법행위 유기](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EC%9C%A0%EA%B8%B0.gif?raw=true)

### CCTV : 불법행위 감지 기능 (절도)
![불법행위 절도](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EC%A0%88%EB%8F%84.gif?raw=true)

### CCTV : 불법행위 감지 기능 (파손)
![불법행위 파손](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%ED%8C%8C%EC%86%90.gif?raw=true)

### CCTV : 불법행위 감지 기능 (전등 끔)
![불법행위 전등 끔](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EC%A0%84%EB%93%B1-%EB%81%94.gif?raw=true)

### CCTV : 불법행위 감지 기능 (정상)
![불법행위 정상](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EC%A0%95%EC%83%81.gif?raw=true)

### CCTV : 알림 및 클립 재생
![알림 및 클립 재생](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EC%95%8C%EB%A6%BC%20%EB%B0%8F%20%ED%81%B4%EB%A6%BD%20%EB%B3%B4%EA%B8%B0.gif?raw=true)

### Dashboard : 불법행위 통계 조회 기능
![Dashboard 통계 조회](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%ED%86%B5%EA%B3%84%20%EC%A1%B0%ED%9A%8C%20%EA%B8%B0%EB%8A%A5.gif?raw=true)

### Detect Log : 불법 행위 기록 조회 > 필터 기능
![기록조회 필터 기능](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EA%B8%B0%EB%A1%9D%EC%A1%B0%ED%9A%8C%20%ED%95%84%ED%84%B0%20%EA%B8%B0%EB%8A%A5.gif?raw=true)

### Detect Log : 불법 행위 기록 조회 > 불법 종류 변경 / 확정 기능
![기록조회 종류 변경 및 확정](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EC%A2%85%EB%A5%98%20%EB%B3%80%EA%B2%BD.gif?raw=true)
 
### Detect Log : 불법 행위 기록 조회 > 클립 삭제 기능
![클립 삭제](https://github.com/addinedu-ros-9th/deeplearning-repo-4/blob/dev/readme_images/%EB%94%94%ED%85%8D%ED%8A%B8%20%EB%A1%9C%EA%B7%B8%20%ED%81%B4%EB%A6%BD%20%EC%82%AD%EC%A0%9C.gif?raw=true)

# 마무리
## 소감
| 이름 | 소감 |
|:---:|---|
| 김범진 | 팀장 역할을 맡으면서 팀원들의 의견을 조율하고 일정과 작업 분담을 관리하며 프로젝트를 이끌어가는 과정에서 많은 책임감을 느꼈습니다. 특히 딥러닝 모델을 학습시키고 결과를 분석하는 과정을 직접 경험하면서, 이론적으로만 알고 있던 딥러닝 구조와 학습 방식에 대해 더 깊이 이해할 수 있었습니다. 또한 프로젝트 전반을 관리하며 전체적인 개발 흐름과 협업의 중요성을 배울 수 있는 값진 경험이 되었습니다. |
| 김채연 | 실시간 영상 송수신을 구현하며 해상도 조절, 패킷 분할 및 재조립 과정을 통해 지연 시간을 최소화하는 경험을 했고, 연속된 동작에 대해 다양한 모델을 활용해 학습하면서 실시간 처리에 필요한 직관과 기술을 체득하였습니다. 또한, 개발 전반에 걸쳐 스크럼 기반의 협업 프로세스를 경험하며 주기적인 피드백과 역할 분담의 중요성을 몸소 느낄 수 있었습니다. | 
| 구민제 | 모델 학습과 시각화에 대한 큰 영감을 얻게 되어 너무 만족스러운 프로젝트였어요. How nice! | 
| 최원호 | GUI를 작업하고 서버와 통신을 하면서 전체적인 통신 과정을 익히게 되었습니다. 또한 딥러닝 코드를 만지게 되면서, 앱에서 사용되는 AI 모델을 어떻게 학습시키는지 알 수 있는 시간이었습니다. AI 서버와 중앙 서버를 분리하면서 트래픽을 분산시켜 처리하고, 각각의 아키텍쳐들의 실제 코드가 어떻게 구성되는지 어떠한 실질적인 역할을 하는지 몸소 와닿는 경험이 되었습니다. | 

