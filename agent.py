"""
Claude API 통합 모듈
Main Agent와 Skill들을 실행합니다.
"""
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class PricingAgent:
    def __init__(self, prompts):
        self.prompts = prompts
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-opus-4-5-20251101"

    def run_skill(self, skill_name, user_input, previous_results=None):
        """개별 Skill을 실행합니다."""
        system_prompt = self.prompts[skill_name]

        # 이전 단계 결과를 포함한 입력 구성
        full_input = user_input
        if previous_results:
            full_input = f"{user_input}\n\n## 이전 단계 분석 결과:\n{previous_results}"

        messages = [
            {
                "role": "user",
                "content": full_input
            }
        ]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            system=system_prompt,
            messages=messages
        )

        return response.content[0].text

    def run_full_analysis(self, user_data, progress_callback=None):
        """전체 가격 정책 분석을 실행합니다."""
        results = {}

        # 사용자 입력 정리
        user_input = f"""
## 제공된 정보

### 제품/서비스 개요
{user_data['product_overview']}

### 비용 구조
**변동비용:**
{user_data['variable_costs']}

**고정비용:**
{user_data['fixed_costs']}

### 예상 사용 패턴
{user_data['usage_pattern']}

### 타겟 고객층
{user_data['target_customers']}

### 사업 목표
{user_data['business_goals']}

### 제약사항
{user_data['constraints']}
"""

        # 1단계: 비용 분석
        if progress_callback:
            progress_callback("1/4 비용 분석 중...")
        results['cost_analysis'] = self.run_skill('cost_analyzer', user_input)

        # 2단계: 시장 조사
        if progress_callback:
            progress_callback("2/4 시장 가격 조사 중...")
        results['market_research'] = self.run_skill(
            'market_researcher',
            user_input,
            results['cost_analysis']
        )

        # 3단계: 가격 모델 설계
        if progress_callback:
            progress_callback("3/4 가격 모델 설계 중...")
        previous = f"## 비용 분석 결과\n{results['cost_analysis']}\n\n## 시장 조사 결과\n{results['market_research']}"
        results['pricing_model'] = self.run_skill(
            'pricing_designer',
            user_input,
            previous
        )

        # 4단계: 재무 검증
        if progress_callback:
            progress_callback("4/4 재무 시뮬레이션 중...")
        previous = f"## 비용 분석 결과\n{results['cost_analysis']}\n\n## 가격 모델\n{results['pricing_model']}"
        results['financial_simulation'] = self.run_skill(
            'financial_simulator',
            user_input,
            previous
        )

        # 5단계: Main Agent를 통한 최종 권고
        if progress_callback:
            progress_callback("최종 권고안 작성 중...")

        final_input = f"""
{user_input}

## 분석 완료 결과

### 비용 분석
{results['cost_analysis']}

### 시장 조사
{results['market_research']}

### 가격 모델 설계
{results['pricing_model']}

### 재무 시뮬레이션
{results['financial_simulation']}

위 모든 분석 결과를 통합하여 최종 권고안을 작성해주세요.
2-3개의 가격 정책 옵션을 제시하고, 각 옵션의 장단점과 추천 옵션을 명확히 제시해주세요.
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            system=self.prompts['main_agent'],
            messages=[{"role": "user", "content": final_input}]
        )

        results['final_recommendation'] = response.content[0].text

        return results
