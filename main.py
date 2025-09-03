#!/usr/bin/env python3
"""
질문 분해 도구 메인 스크립트

이 스크립트는 긴 질문을 여러 개의 짧은 질문으로 분해하여
멀티턴 대화 형태로 변환하는 기능을 제공합니다.
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from question_splitter import process_dataset

# .env 파일에서 환경변수 로드
load_dotenv()

def main():
    parser = argparse.ArgumentParser(
        description="긴 질문을 여러 개의 짧은 질문으로 분해하는 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main.py input.json output.json
        """
    )
    
    parser.add_argument('input_file', help='입력 JSON 파일 경로')
    parser.add_argument('output_file', help='출력 JSON 파일 경로')
    parser.add_argument('--api-key', help='OpenAI API 키 (환경변수 대신 사용)')
    
    args = parser.parse_args()
    
    # API 키 확인
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API 키가 필요합니다.")
        print("💡 .env 파일에 OPENAI_API_KEY 설정하거나")
        print("환경변수로 설정: export OPENAI_API_KEY='your-api-key'")
        print("또는 --api-key 옵션을 사용하세요.")
        sys.exit(1)
    
    try:
        if not os.path.exists(args.input_file):
            print(f"❌ 파일을 찾을 수 없습니다: {args.input_file}")
            sys.exit(1)
        print(f"📊 데이터셋 처리 시작...")
        print(f"📁 입력: {args.input_file}")
        print(f"📁 출력: {args.output_file}")
        process_dataset(args.input_file, args.output_file, api_key)
    
    except KeyboardInterrupt:
        print("\n  사용자에 의해 중단됨")
    except Exception as e:
        print(f" 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
