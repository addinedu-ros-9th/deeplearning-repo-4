[![표지](https://private-user-images.githubusercontent.com/204112513/461314830-a745af10-355b-4bcd-b621-7d02102f60b3.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MjI5MjgsIm5iZiI6MTc1MTQyMjYyOCwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzE0ODMwLWE3NDVhZjEwLTM1NWItNGJjZC1iNjIxLTdkMDIxMDJmNjBiMy5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwMjE3MDhaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1lYTg1OGYyOGYxZTQ5ZDc2NzQxM2RmMWYxMDRjNjBmOGRmNmU5N2UwOWJiYmQ0MDM0MzYwM2Y5YmRkNWFhYzVjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.nvWncj9nivLmENjNo_fcdMdmvCWarL0ji34BdzO1rKE)](https://docs.google.com/presentation/d/1FakMHUjW8QSYNp0pCkSbHC8iK0WQIAL3S_snXaCv-xs/edit?slide=id.g369f27ec0ea_3_0#slide=id.g369f27ec0ea_3_0)
[ㄴ 클릭시 PPT 이동](https://docs.google.com/presentation/d/1FakMHUjW8QSYNp0pCkSbHC8iK0WQIAL3S_snXaCv-xs/edit?slide=id.g369f27ec0ea_3_0#slide=id.g369f27ec0ea_3_0)

## 주제 : 무인매장 CCTV 단속 시스템 [딥러닝 프로젝트]
![예시 이미지](https://private-user-images.githubusercontent.com/204112513/461318023-9e671fd0-ca93-45d2-aa70-95f0f8497664.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MjM0NjAsIm5iZiI6MTc1MTQyMzE2MCwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzE4MDIzLTllNjcxZmQwLWNhOTMtNDVkMi1hYTcwLTk1ZjBmODQ5NzY2NC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwMjI2MDBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1iYTRlYmM1ZmEyNjVkYzY3YmJlNWFiMzkzYjg1NTc5YzVlYTllNjI2MDhhNTgwMWQxZjZhY2U0Yzc4NjU0MWEwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.ojLxJFKrpcaY26GR_JPcwzgmH5piNg_k3cdZJiQHoQk)

### 목차
**00** 팀 소개 <br/>
**01** 프로젝트 소개 <br/>
**02** 프로젝트 설계 <br/>
**03** 프로젝트 구현 <br/>
**04** 프로젝트 결과 <br/>
마무리

# 00. 팀 소개
### 팀명 : GIGACHAD
![로고](https://private-user-images.githubusercontent.com/204112513/461319225-fc2ec96c-5eb5-488b-8b57-26ddcc79ef6b.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MjM2NTMsIm5iZiI6MTc1MTQyMzM1MywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzE5MjI1LWZjMmVjOTZjLTVlYjUtNDg4Yi04YjU3LTI2ZGRjYzc5ZWY2Yi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwMjI5MTNaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1hYjZlNmQwMDI4MTc0OGY1M2FhNjI2ZTMxYjRkYzFlYjM0ZTUzZTVhOWRmNjhlODIzYzE0NTIxNThkYTU2NDViJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.q2hxkDe2qjtI5FrVs6jpbqWwoAgTiIutSXX-fQrH0Bo)

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
![일정](https://private-user-images.githubusercontent.com/204112513/461326107-d7448ebe-2d04-4887-b675-4b90f57b0f83.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MjUyNTEsIm5iZiI6MTc1MTQyNDk1MSwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzI2MTA3LWQ3NDQ4ZWJlLTJkMDQtNDg4Ny1iNjc1LTRiOTBmNTdiMGY4My5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwMjU1NTFaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT03ZTczMGVhZjEyYzM2YzRkMDE5NGIyMmY1MzAzYTMxMjUzZmM1N2NjNDkzOGFiOTk1YTUxNTQ2ODJiYThhZTk0JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.oyYZuchZVxu003PdKItGuNOWm6lM3T5QB-qOqd4EHhM)

**25.5.27 ~ 25.7.1 약 5주간 진행** <br/>
**Sprint1** : 기능정의 및 기술조사 <br/>
**Sprint2** : 기술조사 및 설계 <br/>
**Sprint3** : 기술 및 설계 검토 <br/>
**Sprint4** : 구현 및 1차 연동테스트 <br/>
**Sprint5** : 구현 및 2차 연동테스트 <br/>
**Sprint6** : 전체 연동테스트 

# 01. 프로젝트 소개
### 주제 선정 배경
![주제 선정 배경1](https://private-user-images.githubusercontent.com/204112513/461326500-10ceb16d-2370-457c-ae4f-fbbbc3a60417.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MjUzNzcsIm5iZiI6MTc1MTQyNTA3NywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzI2NTAwLTEwY2ViMTZkLTIzNzAtNDU3Yy1hZTRmLWZiYmJjM2E2MDQxNy5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwMjU3NTdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT03ZmZlMjk2YTUwNGEyNDc4M2Q1MzRkZTY1NTNkMTI5N2Y5ZDYxN2UxZmI3YjQ4ODY4MTg1YWZiYTgyODAyMzVkJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.UCstKd-4mFXZMQLPl0mTT4Y3yaBbtW77XdAwt1flgC0)

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

[ **요약** ]
![사용자 요구사항](https://private-user-images.githubusercontent.com/204112513/461328845-fc401a04-746d-4225-bddd-966c957b6396.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MjYxMzAsIm5iZiI6MTc1MTQyNTgzMCwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzI4ODQ1LWZjNDAxYTA0LTc0NmQtNDIyNS1iZGRkLTk2NmM5NTdiNjM5Ni5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwMzEwMzBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1iMzU1ZGFhMTA2NmZiMzA2NmIyMzM2YTc4YTZlOTk0MDQ1Y2UyN2I2YTYxYWYxOGIzNWVkMTUzYjE1YjYyNzRkJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.DhK3kakHAyPPgdmb14esYINRazYaul-XdLEySGyFta0)

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

![System Requirements](https://private-user-images.githubusercontent.com/204112513/461356659-20bf5df6-dd91-4c88-83f9-40fd18c57fd6.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzI4MzYsIm5iZiI6MTc1MTQzMjUzNiwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzU2NjU5LTIwYmY1ZGY2LWRkOTEtNGM4OC04M2Y5LTQwZmQxOGM1N2ZkNi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTAyMTZaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1lOWFhMGUwZjQ4ZGMwZDlhZTFiNzliM2UwOTRmYWZmMjExMzAyMjM5NWFhZWQ0ZmMxNzQxYzIzOGQ3NmQ5Mjc1JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.dcjMgWFppTYkW2Pv2qaghTzkYi4Hg8UfZKMmvgxS8gg)

기능 리스트를 요약하면 크게 3가지로 나눌 수 있습니다. <br/>
불법행위 감지 기능 / 통계 시각확 기능 / 기록 및 클립 조회 기능 

### 서비스 흐름
![서비스 흐름](https://private-user-images.githubusercontent.com/204112513/461357959-4e086db5-41ee-4d54-a2df-bbb911a4ddb7.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzMyNDgsIm5iZiI6MTc1MTQzMjk0OCwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzU3OTU5LTRlMDg2ZGI1LTQxZWUtNGQ1NC1hMmRmLWJiYjkxMWE0ZGRiNy5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTA5MDhaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT04ZjA4YmZkNDNkMjAzZTliZGExZTc0ODdmMGUwZmJhYTE5NjRhM2JmMGVmMmQzMmY1ODU5ZjE2YmQ0M2E4ZTI5JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.U-ZfrQujr1B2zOOHsx0Dc3NcX2bcO-kDIrP_QOf5Heg)

### System Architecture
![System Architecture](https://private-user-images.githubusercontent.com/204112513/461358163-6e4e25c4-34b8-49ad-9e35-ce921218b81e.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzMyNDgsIm5iZiI6MTc1MTQzMjk0OCwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzU4MTYzLTZlNGUyNWM0LTM0YjgtNDlhZC05ZTM1LWNlOTIxMjE4YjgxZS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTA5MDhaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0xODM1MzI1NzdhZjIxYjVkNTM1NDUxYmE4OTJiNWQwMWU5NTIzMTg1Zjk2NjdiMDNhZjk2NTIxMTk0YTAyYmUzJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.mNFubTYJCRngZ6MTF9mxdVwWbMQt7uwcKnrFfFDoupk)

### 시퀀스 다이어그램

<details>
<summary>SC-01 : 불법행위 감지 및 관리자 알림 및 영상 자동저장 [클릭] </summary>

![SC-01](https://private-user-images.githubusercontent.com/204112513/461358851-79a655ff-db99-4de0-b3c1-3bdd84662565.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzM0NTMsIm5iZiI6MTc1MTQzMzE1MywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzU4ODUxLTc5YTY1NWZmLWRiOTktNGRlMC1iM2MxLTNiZGQ4NDY2MjU2NS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTEyMzNaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0zYmJiYTJmNzU0NDcyZjU4ZWE5OTEyZmUyMWIzZDNlZWNlN2U5NzdlODg4YmEyMjRjMWIzMDhjYzVhMTRjY2Y5JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.5Vst-354DT8CAZ0pcv8RqKAxtfGW-s2v0FmoYXXuJmY)

</details>

<details>
<summary> SC-02 : 불법행위 영상 검토 및 다시보기 [클릭] </summary>

![SC-02](https://private-user-images.githubusercontent.com/204112513/461358873-8255f79d-e676-448e-bba1-b26cad0026e0.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzM0NTMsIm5iZiI6MTc1MTQzMzE1MywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzU4ODczLTgyNTVmNzlkLWU2NzYtNDQ4ZS1iYmExLWIyNmNhZDAwMjZlMC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTEyMzNaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT02MmQ3ODdkOTBkNTQxZjU4MTY4ODJjOTEzNjQ5ZTA4MjdhOWQ2NmFiYTNiNjg0NjdlNDg0ZjNkZGVmNDg5Yjc0JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.dRTReZtQUolqytwcMWSRaEufycn9G0_hN-KjTvWZqnU)

</details>

<details>
<summary> SC-03 : CCTV 실시간 모니터링 [클릭] </summary>

![SC-03](https://private-user-images.githubusercontent.com/204112513/461358912-26a95e4c-cd08-4d07-a499-b9799ebdcb6d.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzM0NTMsIm5iZiI6MTc1MTQzMzE1MywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzU4OTEyLTI2YTk1ZTRjLWNkMDgtNGQwNy1hNDk5LWI5Nzk5ZWJkY2I2ZC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTEyMzNaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1lODBjYWRkMTg3MDE4ZTJmYjQxOGE3ODQzYTIzYTA2N2YzMGIxZWVlZTY4YTQ4NTg3ZDk3YmEzMDY2MDUyZTQyJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.ibj06igh3HlwSbzkDAhRdixZmZruA78Dj2fvqKCGxyw)

</details>

<details>
<summary> SC-04 : 불법행위 통계 데이터 생성 및 조회 [클릭] </summary>

![SC-04](https://private-user-images.githubusercontent.com/204112513/461358958-b6725001-6ae3-4b96-8a43-15089fc340b5.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzM0NTMsIm5iZiI6MTc1MTQzMzE1MywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzU4OTU4LWI2NzI1MDAxLTZhZTMtNGI5Ni04YTQzLTE1MDg5ZmMzNDBiNS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTEyMzNaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1jNTg2ODQ1OWNkMDc1YTExMTM3MjdkMzA5YjgyYjRiYmUwZGY4YWViOGZjZDgxZWRjMTQzOTU3ZTZiOGQ5NTc4JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.qdMAar8YGjd5Ug2FKG915ji0oZPuXhdFbxbW3pI6Jns)

</details>

### ERD
![ERD](https://private-user-images.githubusercontent.com/204112513/461360422-963b898a-d6fc-499b-8761-1a478f11f5ef.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzM4NTgsIm5iZiI6MTc1MTQzMzU1OCwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzYwNDIyLTk2M2I4OThhLWQ2ZmMtNDk5Yi04NzYxLTFhNDc4ZjExZjVlZi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTE5MThaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT00NWExYWZlNmNlYTFjNWRjZmNjYWIwYWE4YjQ5MTBkZjJiMzFhMGQyNjMyYjY3ZTQ1YjZiNzExODk5ZjhjYzZmJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.DuxK2XDQ-nth0zrE6_o0Z88CNrV9qnL-kwjL6g9ixv8)

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
![데이터 전처리1](https://private-user-images.githubusercontent.com/204112513/461364496-8bd3efc4-9865-42ca-9292-b800170b68f4.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzQ5NzksIm5iZiI6MTc1MTQzNDY3OSwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzY0NDk2LThiZDNlZmM0LTk4NjUtNDJjYS05MjkyLWI4MDAxNzBiNjhmNC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTM3NTlaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT04MjdkYzdjNmRlMGQ1Mjg2YTIxM2EyNjU5OWNhODY4MmRjZTE3ODViNjYxZGFlZGEzNjg4Nzg5ZjhkZjZjOWJlJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.AsX6Odv1_QQ-o3xbrMNYL4wjPYk1-gvp3VE0jRY7beU)

![데이터 전처리2](https://private-user-images.githubusercontent.com/204112513/461364656-39e4a10a-63d8-498c-b435-46b707b4273b.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzQ5NzksIm5iZiI6MTc1MTQzNDY3OSwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzY0NjU2LTM5ZTRhMTBhLTYzZDgtNDk4Yy1iNDM1LTQ2YjcwN2I0MjczYi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTM3NTlaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0zNTJlNmU0YWNhZWIxNjZmYmNlNWQ3ZmU4ZDM0ZjZiZDQyMGJkYWMwYmEzMDhlNzY4ZDVkNzYwNDEyOWM5MjVhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.aqgEfPAFyN2QcL8-QHStcPhPyCT94YH4NgQEARMUnBc)

![데이터 전처리3](https://private-user-images.githubusercontent.com/204112513/461364635-73e68c97-e7cf-4c77-a016-63d551b5cd4b.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzQ5NzksIm5iZiI6MTc1MTQzNDY3OSwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzY0NjM1LTczZTY4Yzk3LWU3Y2YtNGM3Ny1hMDE2LTYzZDU1MWI1Y2Q0Yi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTM3NTlaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT04MjUwNzUyYjhjZDZkODJkOTYzMzU5ZjE5YTZiZGRjOTIwNDhlNWVkZDgyZWEzYTdjMjNkZmFjNWEzYTY1YjgwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.KOgSLNVsndsz2-oW37CV3b6lH0lEB4qyXm6C0KQUlNs)

데이터 전처리 과정은 
- 영상 촬영 (행위 별로 100개씩 총 400개 영상)
- 영상 컷 편집 (불법 행위 장면만 남기기)
- 관절점 추출 및 정규화 및 시퀀스 구성

순으로 진행되었습니다.

### 딥러닝 모델 선발 과정
![딥러닝 모델 선발 과정](https://private-user-images.githubusercontent.com/204112513/461366740-c74273eb-d80a-4c72-814c-dc0647bc13a1.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzU0OTksIm5iZiI6MTc1MTQzNTE5OSwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzY2NzQwLWM3NDI3M2ViLWQ4MGEtNGM3Mi04MTRjLWRjMDY0N2JjMTNhMS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTQ2MzlaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT02Yzc0MmMwYWIyYTY3ODIyYjUzNjI1YjY0YzU4OTBlNGI1MzM2ZjE1NGFmNzE0YjY0MjUwZWFiOTJlMWRmNTIxJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.7QgSJTb1UMg8gYgoZBLUy_PuPk9TBLA-vdzOnHAX6Ow)

![딥러닝 모델 선발 과정2](https://private-user-images.githubusercontent.com/204112513/461367224-5c4ff264-d8dd-4a27-a0de-fd2ebe4662dc.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzU2ODUsIm5iZiI6MTc1MTQzNTM4NSwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzY3MjI0LTVjNGZmMjY0LWQ4ZGQtNGEyNy1hMGRlLWZkMmViZTQ2NjJkYy5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTQ5NDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT03MzRmNzdmYzdiNDc5ZDIwOTE4M2NiNWJlMDVkM2QxMzg1YzhjMTdjMjk3NWI5NTFhNmE1ODgyMTNmYjhjOGNlJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.yuEkNofehp6NhDWs3aIBLRvfzLfEL9Vb7CUu4UFrY-Y)

![딥러닝 모델 구조1](https://private-user-images.githubusercontent.com/204112513/461367371-c3555f65-ec5f-4817-80b5-1b7b302a4580.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzU2ODUsIm5iZiI6MTc1MTQzNTM4NSwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzY3MzcxLWMzNTU1ZjY1LWVjNWYtNDgxNy04MGI1LTFiN2IzMDJhNDU4MC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTQ5NDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT02ODk0MDRmNGM3NDZkNzYxZmFkNDYwMTYzZDdiYTgwZjM1MzUwOTUxN2NiYjMxYWE5NjYxM2VmMGE0OTQ5ZGIzJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.QyBEJZqxm25UaQNm8bZcO19nXcWIq5Yw8JGzzkOQYRU)

![딥러닝 모델 구조2](https://private-user-images.githubusercontent.com/204112513/461367445-1f5fa87b-faa3-4b45-8687-3ebc4c9d7e48.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzU2ODUsIm5iZiI6MTc1MTQzNTM4NSwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzY3NDQ1LTFmNWZhODdiLWZhYTMtNGI0NS04Njg3LTNlYmM0YzlkN2U0OC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTQ5NDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1mMWFmNmE1ZDNjZTM1MTA2Y2VkNjU1Mzk0MWU1YTZkOTE2ZTVmOTczNDcwMjVmZTNjYmUyMThiYjgyNTIyOTQwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.Kyx-wwHNa8iF1-jHBk-DW2uAHSStE6V5HrzJlooVu14)

![딥러닝 학습 결과](https://private-user-images.githubusercontent.com/204112513/461367543-da20b345-f323-4d6a-a245-e9cadafb5f44.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzU2ODUsIm5iZiI6MTc1MTQzNTM4NSwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzY3NTQzLWRhMjBiMzQ1LWYzMjMtNGQ2YS1hMjQ1LWU5Y2FkYWZiNWY0NC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTQ5NDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0xZWVkZmM2ZTk4NzE3MjcxOGI0MDVhY2I4ODIzMGVhN2NhNmJhMTE5MTVlM2YyMTQ5YjU4ZmQ5YTE0OTZhZGI4JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.sX_voI6kjDAPBT4sQB-3aDK1QGL07dF_ucj4Nmon1dA)

### GUI
GUI 파일 구조

![gui 파일 구조](https://private-user-images.githubusercontent.com/204112513/461368321-3a2c1bba-d168-470e-b0df-63f2aa910c60.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzYxNjIsIm5iZiI6MTc1MTQzNTg2MiwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzY4MzIxLTNhMmMxYmJhLWQxNjgtNDcwZS1iMGRmLTYzZjJhYTkxMGM2MC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNTU3NDJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT00NjM0MTc2MzAzM2Y4ODIzNDNhMWM3ZGUyNzU3MTBmMDM2MWQwOTZiZGI3NmUxNzhkYTc2M2RjMDlkMjIxOTMxJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.fet30b28syktBphnXYh8khI342YGCn5LQDrkUM6hHtQ)

진입점 : main.py <br/>
화면 전환 : main을 통해 login.py <-> layout.py <br/>
layout 의 컴포넌트 : cctv / dashboard / detect_log <br/>
팝업 : video_popup <br/>
스타일 : style.py 에서 모든 qss파일 임포트해옴 <br/>

#### 화면 구성도 : 로그인
![화면 구성도 로그인](https://private-user-images.githubusercontent.com/204112513/461369418-0527e9dd-4cd7-450b-91cb-6a4e4edabb0e.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzY4OTYsIm5iZiI6MTc1MTQzNjU5NiwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzY5NDE4LTA1MjdlOWRkLTRjZDctNDUwYi05MWNiLTZhNGU0ZWRhYmIwZS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjA5NTZaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT04M2FjMmMwZmZkMDYyNDQ3Zjc3N2IzMjdmYjQ0YTM1NTZkOGI3YTdjNjFmZjIxODg3NzE3ZTZiNDFlYWJlMmM3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9._SOBBtVG6zOO5tsNZoSfmI4vGV5SmAQIbsS8JTtjsfk)

#### 화면 구성도 : CCTV
![화면 구성도 CCTV](https://private-user-images.githubusercontent.com/204112513/461369498-a2940285-34c7-4b86-b2a0-46b6a59e7d2b.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzY4OTYsIm5iZiI6MTc1MTQzNjU5NiwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzY5NDk4LWEyOTQwMjg1LTM0YzctNGI4Ni1iMmEwLTQ2YjZhNTllN2QyYi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjA5NTZaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0yNGM5ZjZhMjY0MTZiZmM2NzgyYTNjZWZmZGRlNTAyZmUzYjUyMTQ1YzgyNDUwNGNhZDlkYTllMjlmYWUzYTBjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.A88ev3wSi7EjHNPP8LN_YBNWSGAK7rHGxlvImFy5Y4E)

#### 화면 구성도 : Dashboard
![화면 구성도 Dashboard](https://private-user-images.githubusercontent.com/204112513/461369588-87d1042c-b942-4149-9ddf-44eab967a1e4.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzY4OTYsIm5iZiI6MTc1MTQzNjU5NiwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzY5NTg4LTg3ZDEwNDJjLWI5NDItNDE0OS05ZGRmLTQ0ZWFiOTY3YTFlNC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjA5NTZaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1jNmY2ZDZmYzFjMGM3MzFkMDBjNDJlNTczNmIxNTI2NmFjNTAxMjBmYjYyZmJhNzZlNGMzMzU0YWIwNzMyYWI1JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.89BRonniNzDiN2i9kh2OBlnP-1pgenGo5xbTa65mVGU)

#### 화면 구성도 : Detect Log
![화면 구성도 Detect Log](https://private-user-images.githubusercontent.com/204112513/461369686-2efe084b-c8ec-4c94-a12b-eb394c98130d.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0MzY4OTYsIm5iZiI6MTc1MTQzNjU5NiwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzY5Njg2LTJlZmUwODRiLWM4ZWMtNGM5NC1hMTJiLWViMzk0Yzk4MTMwZC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjA5NTZaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0wMzRkOTBiMDkwNzI5Yjk0MjVjMWUyOTBmYjk5OTRmYzBmODQ2MTJiYjllZjk2NTY1NWViNWIzMzI4ZmY5ZTYwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.jXaCNs_iF2CdF1o1tVlEj3ziO7pHNNQRS0oRSqeWPYc)

# 04. 프로젝트 결과
### 로그인 기능
![로그인 기능](https://private-user-images.githubusercontent.com/204112513/461377564-159b5e32-998a-46d0-9f5f-0d64b1dda0bb.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0Mzk1NDcsIm5iZiI6MTc1MTQzOTI0NywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzc3NTY0LTE1OWI1ZTMyLTk5OGEtNDZkMC05ZjVmLTBkNjRiMWRkYTBiYi5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjU0MDdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1lZWMwOWQ2ZjllZTA2NzNhNGFjZmNiOWQ5MTgzOWU5NGYyZTdlYTYwOTgyMzk0ODcyYWMxZGE0YmI3OGI4NDFmJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.KRqtYYHRl1kM5r_wZwZyzj0IEG5wDkbf3TH3yoyn6AI)

### CCTV : 불법행위 감지 기능 (유기)
![불법행위 유기](https://private-user-images.githubusercontent.com/204112513/461380730-aca81f4d-1c98-4e26-805b-1981cdc8cf17.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0Mzk1NDcsIm5iZiI6MTc1MTQzOTI0NywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzgwNzMwLWFjYTgxZjRkLTFjOTgtNGUyNi04MDViLTE5ODFjZGM4Y2YxNy5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjU0MDdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT02MDVkZGMzMTQ5NWY1MTIyNWY5YmQ2Y2FkZmYyOWQzMmU2ZWNhODQ5MTNkZTg4ZTNjYzkyYmYyOTNjNzQxNjFhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.7FbvyvdiSs-iDRJRNHy42Auzq5WubUpKc7nfZP7DPA4)

### CCTV : 불법행위 감지 기능 (절도)
![불법행위 절도](https://private-user-images.githubusercontent.com/204112513/461381221-8f457c82-1dd6-4b11-8009-31213a44b87e.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0Mzk1NDcsIm5iZiI6MTc1MTQzOTI0NywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzgxMjIxLThmNDU3YzgyLTFkZDYtNGIxMS04MDA5LTMxMjEzYTQ0Yjg3ZS5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjU0MDdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0xZmJhMzkzMDRkY2FjYTA1ZTdkMmUyMTAzZTRiYzQ5YmM4OTMyNTc0N2VjZjVmYWJjZjk4Y2E4NTk2ZDJmMGM1JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.O7gis0UzLjpPYAF9_6pezYc-_K7u8qiZ-XfusdhLKzQ)

### CCTV : 불법행위 감지 기능 (파손)
![불법행위 파손](https://private-user-images.githubusercontent.com/204112513/461381820-d5d31aac-46ae-4d35-b2e2-6b0f56414e83.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0Mzk1NDcsIm5iZiI6MTc1MTQzOTI0NywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzgxODIwLWQ1ZDMxYWFjLTQ2YWUtNGQzNS1iMmUyLTZiMGY1NjQxNGU4My5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjU0MDdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1kNDczMTY2MzdmNDdlMzk2ODczN2FkYzY5YmNjMDJkMzJhMzY4ZGFiZDhjY2M5YjMwNDMyMDI0ZDQ1MDc1ZWNhJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.3fbFPkzxTkPqm0nNHrTgxn0RwUIU4o37FmJPrMs88HI)

### CCTV : 불법행위 감지 기능 (전등 끔)
![불법행위 전등 끔](https://private-user-images.githubusercontent.com/204112513/461387745-f9704761-12a8-4365-a74c-c89f1c2b4681.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0Mzk1NDcsIm5iZiI6MTc1MTQzOTI0NywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzg3NzQ1LWY5NzA0NzYxLTEyYTgtNDM2NS1hNzRjLWM4OWYxYzJiNDY4MS5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjU0MDdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1lMWE2ZjcxNmQ4YzgyNmYzYWFhNWI2NTBmNDJjZjRhMTcwZTU2NzRmM2ViODRhZTJjZDY0M2ZmOGEwOGM1MTZjJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.FBAcanpvG9mGLJhbqfP1Q1Og6x_ff2N1_NPe-L_SPVY)

### CCTV : 불법행위 감지 기능 (정상)
![불법행위 정상](https://private-user-images.githubusercontent.com/204112513/461381526-ce4e1a20-4634-4ece-bbed-7ea6f7ad984a.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0Mzk1NDcsIm5iZiI6MTc1MTQzOTI0NywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzgxNTI2LWNlNGUxYTIwLTQ2MzQtNGVjZS1iYmVkLTdlYTZmN2FkOTg0YS5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjU0MDdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1kYmYyMDNmZTkwZmViYzUyNTNiNTgwYzIzMmUyZTg1MTYzMmM5YmZkYjkxNjI2YTFmZDg0MjU3ZTdkOWQ2MDQ3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.ZEs-XoDN_obB8LC26hUgRA23AC7w7aNaHD8eJKUHaTo)

### CCTV : 알림 및 클립 재생
![알림 및 클립 재생](https://private-user-images.githubusercontent.com/204112513/461387271-7dade12f-8472-45c2-af48-2027dbe0adb0.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0Mzk1NDcsIm5iZiI6MTc1MTQzOTI0NywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzg3MjcxLTdkYWRlMTJmLTg0NzItNDVjMi1hZjQ4LTIwMjdkYmUwYWRiMC5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjU0MDdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT04NWE2NjA4NTc0NjdhOTgzZWU0OWY4ZjRlNDAyNDZiMWU5MmI3ZTI3MzQyYmVjNGMwYjZhNGZiNzg3MTA5YmVmJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.SApGgpyfgiFPEe4VJA3MQDRrO7E0TOdILglqG2hZct0)

### Dashboard : 불법행위 통계 조회 기능
![Dashboard 통계 조회](https://private-user-images.githubusercontent.com/204112513/461376169-d483c804-171a-4ce5-bfa9-f717d7411f84.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0Mzc1MzQsIm5iZiI6MTc1MTQzNzIzNCwicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzc2MTY5LWQ0ODNjODA0LTE3MWEtNGNlNS1iZmE5LWY3MTdkNzQxMWY4NC5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjIwMzRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT05Nzk1YmI0NWM5MWE1Y2EwMGEyMmFjMjVjYmM2OGQwZmQ2OGM4NjI4YmQ1YmE2Y2RjNTIwZmM2YzViN2RhMjk0JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.XfQonhu5HNXAl_D8gE6vNXHWpNo9GWjYtIiXeNygqMg)

### Detect Log : 불법 행위 기록 조회 > 필터 기능
![기록조회 필터 기능](https://private-user-images.githubusercontent.com/204112513/461382220-1ddcbcac-fdd6-41aa-972f-5c7c51a94496.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0Mzk1NDcsIm5iZiI6MTc1MTQzOTI0NywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzgyMjIwLTFkZGNiY2FjLWZkZDYtNDFhYS05NzJmLTVjN2M1MWE5NDQ5Ni5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjU0MDdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT00NmI1M2E3Yjk1NjY4NDU1ZGRmNGU5MGUxMzJlZGNkMWM0NzA5YTA1MzE5MTcyMzBlYjVhNWJlMjVmNzUyMTA3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.hn1oOlGKL4JXeJoPtV3OOsXEsiQYV8aMC6Pfis015ps)

### Detect Log : 불법 행위 기록 조회 > 불법 종류 변경 / 확정 기능
![기록조회 종류 변경 및 확정](https://private-user-images.githubusercontent.com/204112513/461388948-e3d0385a-d8e3-423c-9a91-4ceb01d372c1.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0Mzk1NDcsIm5iZiI6MTc1MTQzOTI0NywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzg4OTQ4LWUzZDAzODVhLWQ4ZTMtNDIzYy05YTkxLTRjZWIwMWQzNzJjMS5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjU0MDdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT02OThhOTIzZmE4YTk4Y2Q0MTJkOWMyMTBmZWY2MmNlYThiYWE5MWYzODFmM2VlYzk2NjM1YmVhNTc5NmVmZjk2JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.GrCBXcqQgW6nPAtp0axLNkfDivhEjuuY7AI2PNUwBc4)
 
### Detect Log : 불법 행위 기록 조회 > 클립 삭제 기능
![클립 삭제](https://private-user-images.githubusercontent.com/204112513/461383159-45f97a79-0df8-4682-8dbc-5e51368807b4.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTE0Mzk1NDcsIm5iZiI6MTc1MTQzOTI0NywicGF0aCI6Ii8yMDQxMTI1MTMvNDYxMzgzMTU5LTQ1Zjk3YTc5LTBkZjgtNDY4Mi04ZGJjLTVlNTEzNjg4MDdiNC5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMlQwNjU0MDdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1kNzFjYTVlOTJkYTA4NDhhMmJjODA4NmI5NmZjNGJjNzViMTNkNGFmYTdkODVmMDZjNGYwZTAzZDcwOWExOTY1JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.5WyN15zD84ng6tPPr04q2hYH1isgZTRuLz3trEaLtF0)

# 마무리
## 소감
| 이름 | 소감 |
|:---:|---|
| 김범진 |  |
| 김채연 |  | 
| 구민제 |  | 
| 최원호 | GUI를 작업하고 서버와 통신을 하면서 전체적인 통신 과정을 익히게 되었습니다. 또한 딥러닝 코드를 만지게 되면서, 앱에서 사용되는 AI 모델을 어떻게 학습시키는지 알 수 있는 시간이었습니다. AI 서버와 중앙 서버를 분리하면서 트래픽을 분산시켜 처리하고, 각각의 아키텍쳐들의 실제 코드가 어떻게 구성되는지 어떠한 실질적인 역할을 하는지 몸소 와닿는 경험이 되었습니다. | 