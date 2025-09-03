import json
import openai
import re
from typing import List
import os
from datetime import datetime
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()


class QuestionSplitter:
    """
    긴 질문을 여러 개의 짧은 질문으로 분해하는 클래스
    GPT-4o-mini를 사용하여 멀티턴 대화 형태로 질문을 분해합니다.
    """

    def __init__(self, api_key: str = None):
        """
        QuestionSplitter 초기화

        Args:
            api_key (str): OpenAI API 키. 없으면 환경변수에서 읽음
        """
        if api_key:
            openai.api_key = api_key
        else:
            openai.api_key = os.getenv("OPENAI_API_KEY")

        if not openai.api_key:
            raise ValueError(
                "OpenAI API 키가 필요합니다. 환경변수 OPENAI_API_KEY를 설정하거나 api_key 파라미터를 제공하세요."
            )

    def split_question(self, question: str) -> List[str]:
        """
        질문을 분해할 수 있는지 LLM이 판단하고, 가능하면 여러 개의 짧은 질문으로 분해
        Args: question (str): 분해할 원본 질문
        Returns: List[str]: 분해된 짧은 질문들의 리스트 (분해 불가능하면 원본 질문 반환)
        """
        prompt = f"""
다음 질문을 분석하여 여러 개의 짧은 질문으로 분해할 수 있는지 판단하고, 가능하다면 분해해주세요.

원본 질문: {question}

## 판단 기준:
1. **복합성**: 여러 데이터 요구, 분석+예측 동시 포함, 다단계 처리가 필요한가?
2. **자연스러움**: 멀티턴 대화로 나누면 더 자연스럽고 이해하기 쉬운가?

## 분해 규칙:
**분해가 필요한 경우:**
- 각 질문은 독립적으로 SQL로 답변 가능해야 함
- 이전 질문의 결과를 활용하는 자연스러운 흐름 구성
- 마지막 질문이 원본 질문의 최종 목적을 달성해야 함
- 각 질문은 명확하고 구체적이되, 과도한 맥락 반복은 피함
- 얼마인가요? 누구인가요? 어디인가요 등 생략해도 이해가 되는 표현은 생략가능합니다.

**맥락 생략 가이드:**
- 바로 앞 질문에서 언급된 기간/대상은 "이 데이터를 기반으로", "그렇다면" 등으로 자연스럽게 연결
- 주어(회사, 제품 등)가 계속 동일하면 생략 가능
- 하지만 질문 자체가 이해 불가능할 정도로 생략하지 말 것

**분해 불필요한 경우:**
- 단일 데이터 조회만 필요한 질문
- 이미 충분히 간단하고 명확한 질문  
- 억지로 분해하면 부자연스러워지는 질문

## 예시:

예시 1 (분해 필요)
원본: "최근 5개년의 매출금액과 GM을 기반으로, 향후 5개년간의 예상되는 매출금액과 GM은?"
결과: [
  "최근 5년간의 매출금액",
  "GM은?",
  "그렇다면 이 데이터를 기반으로 향후 5년간 매출액과 GM을 예측해줄 수 있나요?",
]

예시 2 (분해 불필요)
원본: "최근 5년간의 매출금액은?"
결과: [
    "최근 5년간의 매출금액은?"
]

예시 3 (분해 필요)
원본: "최근 3개년 매출금액을 기반으로, 영업대표별 예상되는 상품별 매출금액은?"
결과: [
  "최근 3년간 영업대표들의 상품별 매출금액은?",
  "내년은?",
]

이제 원본 질문을 분석하고 JSON 배열로 결과를 반환해주세요:
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 복잡한 질문을 단계별로 분해하는 전문가입니다. 사용자의 질문을 자연스러운 대화 흐름에 따라 여러 개의 간단한 질문으로 나누어 주세요.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
                temperature=0.3,
            )

            result = response.choices[0].message.content.strip()

            # 빈 응답 확인
            if not result:
                return [question]

            # "NO_SPLIT" 응답 확인
            if "NO_SPLIT" in result:
                return [question]

            # JSON 배열 파싱
            try:
                # 응답에서 JSON 부분 추출 시도
                split_questions = self._extract_json_from_response(result)

                # 결과 검증
                if isinstance(split_questions, list) and len(split_questions) > 0:
                    # 모든 요소가 문자열인지 확인
                    if all(isinstance(q, str) and q.strip() for q in split_questions):
                        return split_questions
                    else:
                        print(f"⚠️ 분해된 질문 형식 오류. 문자열이 아닌 요소 발견")
                        return [question]
                else:
                    print(f"⚠️ 분해된 질문이 올바른 배열 형식이 아님")
                    return [question]

            except json.JSONDecodeError as e:
                print(f"JSON 파싱 실패: {e}")
                print(f"응답 내용 (처음 200자): {result[:200]}...")

                return [question]
            except Exception as e:
                print(f"예상치 못한 파싱 오류: {e}")
                return [question]

        except Exception as e:
            print(f"질문 분해 중 오류 발생: {e}")
            return [question]

    def _extract_json_from_response(self, response_text: str):
        """
        응답 텍스트에서 JSON 배열 추출
        """
        # 먼저 전체 텍스트를 JSON으로 파싱 시도
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        json_pattern = r"\[.*?\]"
        matches = re.findall(json_pattern, response_text, re.DOTALL)

        for match in matches:
            try:
                result = json.loads(match)
                if isinstance(result, list):
                    return result
            except json.JSONDecodeError:
                continue

        raise json.JSONDecodeError("JSON 배열을 찾을 수 없음", response_text, 0)


def process_dataset(input_file: str, output_file: str, api_key: str = None):
    """
    JSON 데이터셋을 처리하여 긴 질문들을 분해하고 원본 포맷에 split_questions 필드 추가

    Args:
        input_file (str): 입력 JSON 파일 경로
        output_file (str): 출력 JSON 파일 경로
        api_key (str): OpenAI API 키
    """

    splitter = QuestionSplitter(api_key)

    # 원본 데이터 로드
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    original_count = len(data)

    for i, item in enumerate(data):
        print(f"처리 중... {i+1}/{len(data)}")

        original_question = item["question"]

        # LLM이 질문 분해 가능 여부를 판단하고 분해
        split_questions = splitter.split_question(original_question)

        # 분해된 질문이 1개가 아니거나 원본과 다르면 분해된 것
        if len(split_questions) > 1 or (
            len(split_questions) == 1 and split_questions[0] != original_question
        ):
            # 분해된 경우
            item["split_questions"] = split_questions
            item["is_split"] = True
            item["total_splits"] = len(split_questions)
        else:
            # 분해되지 않은 경우
            item["split_questions"] = [original_question]
            item["is_split"] = False
            item["total_splits"] = 1

    # 새로운 파일에 결과 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"처리 완료! 결과가 {output_file}에 저장되었습니다.")


if __name__ == "__main__":
    pass
