deeplearning-repo-4/
├── saved_models/       # 모델 저장 폴더
│   └── 
├── src/                # 소스 코드 폴더
│   ├── models/         # 모델 관련 파일 폴더
│   │   └── 
│   ├── trains/         # 학습 관련 코드 폴더
│   │   ├── abandon_train.py    # 유기
│   │   ├── broken_train.py     # 파손
│   │   ├── lightoff_train.py   # 전등 끔
│   │   └── theft_train.py      # 절도
│   ├── utils/          # 유틸리티 코드 폴더
│   │   ├── logger.py           # 학습 로그 저장
│   │   ├── metrics.py          # 정확도 f1-score 등 평가 지표 계산
│   │   └── visualizer.py       # 결과 시각화 (matplotlib 등)
├── forder_structure.md # 폴더 구조 설명 파일
├── README.md           # 프로젝트 설명 파일

export PYTHONPATH=/home/wonho/deeplearning-repo-4/src:$PYTHONPATH