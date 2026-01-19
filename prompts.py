"""
프롬프트 로더 모듈
saas_pricing_prompts.md 파일에서 Main Agent와 Skill 프롬프트를 추출합니다.
"""
import re

def load_prompts():
    """saas_pricing_prompts.md에서 모든 프롬프트를 로드합니다."""
    with open('saas_pricing_prompts.md', 'r', encoding='utf-8') as f:
        content = f.read()

    prompts = {}

    # Main Agent 프롬프트 추출
    main_agent_match = re.search(
        r'## Main Agent: 가격 정책 컨설턴트\s*```markdown\s*(.*?)\s*```',
        content,
        re.DOTALL
    )
    if main_agent_match:
        prompts['main_agent'] = main_agent_match.group(1).strip()

    # Skill 1: 비용 분석기
    skill1_match = re.search(
        r'## Skill 1: 비용 분석기\s*```markdown\s*(.*?)\s*```',
        content,
        re.DOTALL
    )
    if skill1_match:
        prompts['cost_analyzer'] = skill1_match.group(1).strip()

    # Skill 2: 시장 가격 조사기
    skill2_match = re.search(
        r'## Skill 2: 시장 가격 조사기\s*```markdown\s*(.*?)\s*```',
        content,
        re.DOTALL
    )
    if skill2_match:
        prompts['market_researcher'] = skill2_match.group(1).strip()

    # Skill 3: 가격 모델 설계기
    skill3_match = re.search(
        r'## Skill 3: 가격 모델 설계기\s*```markdown\s*(.*?)\s*```',
        content,
        re.DOTALL
    )
    if skill3_match:
        prompts['pricing_designer'] = skill3_match.group(1).strip()

    # Skill 4: 재무 시뮬레이터
    skill4_match = re.search(
        r'## Skill 4: 재무 시뮬레이터\s*```markdown\s*(.*?)\s*```',
        content,
        re.DOTALL
    )
    if skill4_match:
        prompts['financial_simulator'] = skill4_match.group(1).strip()

    return prompts
