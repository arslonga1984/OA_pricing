"""
SaaS 가격 정책 수립 시스템 - 간단한 버전 (API 키 불필요)
사용자 입력을 받아 각 Skill에 사용할 프롬프트를 생성합니다.
"""
import streamlit as st
from prompts import load_prompts

# 페이지 설정
st.set_page_config(
    page_title="SaaS 가격 정책 수립 시스템 (간단 버전)",
    page_icon="💰",
    layout="wide"
)

# 세션 상태 초기화
if 'prompts_loaded' not in st.session_state:
    try:
        st.session_state.prompts = load_prompts()
        st.session_state.prompts_loaded = True
    except Exception as e:
        st.session_state.prompts_loaded = False
        st.session_state.load_error = str(e)

# 헤더
st.title("💰 SaaS 가격 정책 수립 시스템")
st.markdown("### 📋 프롬프트 생성 버전 (API 키 불필요)")
st.markdown("---")

# 프롬프트 로드 확인
if not st.session_state.prompts_loaded:
    st.error(f"프롬프트 파일 로드 실패: {st.session_state.load_error}")
    st.stop()

# 사이드바: 사용 방법
with st.sidebar:
    st.header("📖 사용 방법")
    st.markdown("""
    이 버전은 **API 키 없이** 사용할 수 있습니다.

    ### 작동 방식
    1. 왼쪽 폼에 제품 정보 입력
    2. '프롬프트 생성' 버튼 클릭
    3. 각 단계별 프롬프트가 생성됩니다
    4. 프롬프트를 복사하여 다음에 붙여넣기:
       - ChatGPT (GPT-4)
       - Claude.ai 웹사이트
       - 기타 LLM

    ### 단계별 실행
    1️⃣ 비용 분석 프롬프트 복사
    2️⃣ LLM에 붙여넣고 결과 받기
    3️⃣ 시장 조사 프롬프트 복사
    4️⃣ 반복...

    각 단계의 결과를 다음 단계에 포함시켜야 합니다.
    """)

    st.markdown("---")
    st.info("💡 **Tip**: Claude Opus 4나 GPT-4를 권장합니다.")

# 메인 컨텐츠
st.header("📝 제품 정보 입력")

with st.form("pricing_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. 제품/서비스 개요")
        product_overview = st.text_area(
            "제품 설명",
            placeholder="예: AI 기반 업무 자동화 챗봇으로, 직원들의 반복적인 업무를 자동화하고 생산성을 향상시킵니다.",
            height=100,
            help="제품이 무엇이고, 어떤 문제를 해결하는지 설명해주세요"
        )

        st.subheader("2. 비용 구조")
        variable_costs = st.text_area(
            "변동비용 (사용량에 비례)",
            placeholder="예:\n- GPT-4 API: 사용자당 월 평균 $5\n- AWS 비용: 사용자당 월 $2\n- 총 변동비: 사용자당 월 $7",
            height=100,
            help="LLM API, 클라우드 비용 등 사용량에 따라 변동되는 비용"
        )

        fixed_costs = st.text_area(
            "고정비용 (사용자 수와 무관)",
            placeholder="예:\n- 인건비: 월 2천만원 (개발 3명)\n- 인프라 기본료: 월 50만원\n- 기타: 월 100만원\n- 총 고정비: 월 2,150만원",
            height=100,
            help="인건비, 인프라 기본료 등 고정적으로 발생하는 비용"
        )

    with col2:
        st.subheader("3. 예상 사용 패턴")
        usage_pattern = st.text_area(
            "사용 패턴",
            placeholder="예: 사용자 1인당 월 평균 1,000회 쿼리 예상, 파워유저는 3,000회까지 사용",
            height=80,
            help="사용자당 평균 사용량과 편차"
        )

        st.subheader("4. 타겟 고객층")
        target_customers = st.text_area(
            "타겟 고객",
            placeholder="예: B2B, 직원 50-500명 규모의 중소/중견기업, IT/금융/제조업",
            height=80,
            help="B2B/B2C, 기업 규모, 업종 등"
        )

        st.subheader("5. 사업 목표")
        business_goals = st.text_area(
            "사업 목표",
            placeholder="예: 향후 12개월 내 100개 기업 유치 목표, 초기에는 시장 점유율 확보가 우선",
            height=80,
            help="시장 점유율 vs 수익성, 목표 고객 수 등"
        )

        st.subheader("6. 제약사항")
        constraints = st.text_area(
            "제약사항 및 고려사항",
            placeholder="예: 경쟁사 A의 가격($50/월/인) 대비 경쟁력 있는 가격 필요, Tiered 모델 선호",
            height=80,
            help="가격 제약, 선호하는 모델, 기타 고려사항"
        )

    submitted = st.form_submit_button(
        "🚀 프롬프트 생성",
        use_container_width=True,
        type="primary"
    )

# 프롬프트 생성
if submitted:
    if not all([product_overview, variable_costs, fixed_costs, usage_pattern,
                  target_customers, business_goals]):
        st.error("⚠️ 모든 필수 항목을 입력해주세요")
    else:
        # 사용자 데이터 정리
        user_context = f"""## 제공된 정보

### 제품/서비스 개요
{product_overview}

### 비용 구조
**변동비용:**
{variable_costs}

**고정비용:**
{fixed_costs}

### 예상 사용 패턴
{usage_pattern}

### 타겟 고객층
{target_customers}

### 사업 목표
{business_goals}

### 제약사항
{constraints if constraints else "특별한 제약사항 없음"}
"""

        st.markdown("---")
        st.header("📋 생성된 프롬프트")

        st.info("💡 아래 프롬프트를 **순서대로** ChatGPT, Claude.ai 등에 복사하여 사용하세요. 각 단계의 결과를 다음 단계에 포함시켜야 합니다.")

        # 탭으로 각 Skill 프롬프트 표시
        tabs = st.tabs([
            "1️⃣ 비용 분석",
            "2️⃣ 시장 조사",
            "3️⃣ 가격 모델 설계",
            "4️⃣ 재무 시뮬레이션",
            "5️⃣ 최종 권고"
        ])

        # Skill 1: 비용 분석
        with tabs[0]:
            st.markdown("### 🔢 비용 분석 프롬프트")
            st.markdown("이 프롬프트를 LLM에 복사하여 붙여넣으세요.")

            skill1_prompt = f"""# 시스템 프롬프트
{st.session_state.prompts['cost_analyzer']}

---

# 사용자 요청
{user_context}

위 정보를 바탕으로 비용 분석을 수행해주세요.
"""

            st.code(skill1_prompt, language="markdown")
            st.download_button(
                "📥 비용 분석 프롬프트 다운로드",
                skill1_prompt,
                file_name="1_cost_analysis_prompt.txt",
                mime="text/plain"
            )

            st.markdown("---")
            st.warning("⚠️ **다음 단계**: LLM의 응답을 받은 후, 그 결과를 복사해서 2단계(시장 조사)에 포함시키세요.")

        # Skill 2: 시장 조사
        with tabs[1]:
            st.markdown("### 🔍 시장 가격 조사 프롬프트")
            st.markdown("**1단계(비용 분석) 결과를 아래 `[여기에 1단계 결과 붙여넣기]` 부분에 붙여넣은 후** LLM에 전송하세요.")

            skill2_prompt = f"""# 시스템 프롬프트
{st.session_state.prompts['market_researcher']}

---

# 사용자 요청
{user_context}

## 이전 단계 결과

### 1단계: 비용 분석 결과
[여기에 1단계 결과 붙여넣기]

---

위 정보를 바탕으로 시장 가격 조사를 수행해주세요. 웹 검색을 활용하여 최신 경쟁사 정보를 수집하세요.
"""

            st.code(skill2_prompt, language="markdown")
            st.download_button(
                "📥 시장 조사 프롬프트 다운로드",
                skill2_prompt,
                file_name="2_market_research_prompt.txt",
                mime="text/plain"
            )

        # Skill 3: 가격 모델 설계
        with tabs[2]:
            st.markdown("### 💡 가격 모델 설계 프롬프트")
            st.markdown("**1, 2단계 결과를 모두 포함**한 후 LLM에 전송하세요.")

            skill3_prompt = f"""# 시스템 프롬프트
{st.session_state.prompts['pricing_designer']}

---

# 사용자 요청
{user_context}

## 이전 단계 결과

### 1단계: 비용 분석 결과
[여기에 1단계 결과 붙여넣기]

### 2단계: 시장 조사 결과
[여기에 2단계 결과 붙여넣기]

---

위 비용 분석과 시장 조사 결과를 바탕으로 최적의 가격 모델을 설계해주세요.
"""

            st.code(skill3_prompt, language="markdown")
            st.download_button(
                "📥 가격 모델 설계 프롬프트 다운로드",
                skill3_prompt,
                file_name="3_pricing_model_prompt.txt",
                mime="text/plain"
            )

        # Skill 4: 재무 시뮬레이션
        with tabs[3]:
            st.markdown("### 📊 재무 시뮬레이션 프롬프트")
            st.markdown("**1, 2, 3단계 결과를 모두 포함**한 후 LLM에 전송하세요.")

            skill4_prompt = f"""# 시스템 프롬프트
{st.session_state.prompts['financial_simulator']}

---

# 사용자 요청
{user_context}

## 이전 단계 결과

### 1단계: 비용 분석 결과
[여기에 1단계 결과 붙여넣기]

### 2단계: 시장 조사 결과
[여기에 2단계 결과 붙여넣기]

### 3단계: 가격 모델 설계 결과
[여기에 3단계 결과 붙여넣기]

---

위 분석 결과를 바탕으로 12개월 재무 시뮬레이션을 수행해주세요.
"""

            st.code(skill4_prompt, language="markdown")
            st.download_button(
                "📥 재무 시뮬레이션 프롬프트 다운로드",
                skill4_prompt,
                file_name="4_financial_simulation_prompt.txt",
                mime="text/plain"
            )

        # 최종 권고
        with tabs[4]:
            st.markdown("### 🎯 최종 권고안 프롬프트")
            st.markdown("**모든 단계(1-4)의 결과를 포함**한 후 LLM에 전송하세요.")

            final_prompt = f"""# 시스템 프롬프트
{st.session_state.prompts['main_agent']}

---

# 사용자 요청
{user_context}

## 모든 분석 결과

### 1단계: 비용 분석 결과
[여기에 1단계 결과 붙여넣기]

### 2단계: 시장 조사 결과
[여기에 2단계 결과 붙여넣기]

### 3단계: 가격 모델 설계 결과
[여기에 3단계 결과 붙여넣기]

### 4단계: 재무 시뮬레이션 결과
[여기에 4단계 결과 붙여넣기]

---

위 모든 분석 결과를 통합하여 최종 권고안을 작성해주세요.
2-3개의 가격 정책 옵션을 제시하고, 각 옵션의 장단점과 추천 옵션을 명확히 제시해주세요.
"""

            st.code(final_prompt, language="markdown")
            st.download_button(
                "📥 최종 권고 프롬프트 다운로드",
                final_prompt,
                file_name="5_final_recommendation_prompt.txt",
                mime="text/plain"
            )

        # 전체 다운로드
        st.markdown("---")
        st.markdown("### 📦 전체 프롬프트 다운로드")

        all_prompts = f"""# SaaS 가격 정책 수립 시스템 - 전체 프롬프트

## 사용자 정보
{user_context}

{'='*80}

## 1단계: 비용 분석 프롬프트
{skill1_prompt}

{'='*80}

## 2단계: 시장 조사 프롬프트
{skill2_prompt}

{'='*80}

## 3단계: 가격 모델 설계 프롬프트
{skill3_prompt}

{'='*80}

## 4단계: 재무 시뮬레이션 프롬프트
{skill4_prompt}

{'='*80}

## 5단계: 최종 권고 프롬프트
{final_prompt}
"""

        st.download_button(
            "📥 전체 프롬프트 한번에 다운로드",
            all_prompts,
            file_name="all_prompts.txt",
            mime="text/plain",
            use_container_width=True,
            type="primary"
        )

# 푸터
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>SaaS 가격 정책 수립 시스템 - 간단 버전 (API 키 불필요)</div>",
    unsafe_allow_html=True
)
