복잡하고 긴 질문을 여러 개의 짧은 질문으로 분해하여 멀티턴 대화 형태로 변환하는 도구입니다. GPT-4o-mini를 사용하여 자연스러운 대화 흐름을 만들어냅니다.


## 설치 방법

```bash
# 저장소 클론 또는 파일 다운로드 후
pip install -r requirements.txt
```

## 사용법

### 1. 질문 분해 실행

```bash
python main.py eztobiz_sqlagent_evaluation_dataset_v1.json split_questions_dataset.json
```

### 2. 단일 질문 테스트

```bash
python main.py test "최근 5개년의 매출금액과 GM을 기반으로, 향후 5개년간의 예상되는 매출금액과 GM은?"
```

## 파일 구조

```
eztobiz_multiturn_question_generator/
├── question_splitter.py      # 핵심 질문 분해 클래스
├── main.py                   # 메인 실행 스크립트
├── requirements.txt          # 필요한 패키지 목록
├── README.md                 # 이 파일
└── eztobiz_sqlagent_evaluation_dataset_v1.json  # 입력 데이터
```