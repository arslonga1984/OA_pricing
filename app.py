"""
SaaS 가격 정책 수립 시스템 - Streamlit 앱
"""
import streamlit as st
from prompts import load_prompts
from agent import PricingAgent
import traceback

# 페이지 설정
st.set_page_config(
    page_title="SaaS 가격 정책 수립 시스템",
    page_icon="💰",
    layout="wide"
)

# 세션 상태 초기화
if 'results' not in st.session_state:
    st.session_state.results = None
if 'prompts_loaded' not in st.session_state:
    try:
        st.session_state.prompts = load_prompts()
        st.session_state.prompts_loaded = True
    except Exception as e:
        st.session_state.prompts_loaded = False
        st.session_state.load_error = str(e)

# 헤더
st.title("💰 SaaS 가격 정책 수립 시스템")
st.markdown("---")

# 프롬프트 로드 확인
if not st.session_state.prompts_loaded:
    st.error(f"프롬프트 파일 로드 실패: {st.session_state.load_error}")
    st.stop()

# 사이드바: API 키 설정
with st.sidebar:
    st.header("⚙️ 설정")

    # API 키 입력
    st.markdown("### Anthropic API Key")
    st.markdown("[API 키 발급받기](https://console.anthropic.com/)")

    import os
    from dotenv import load_dotenv
    load_dotenv()

    default_key = os.getenv('ANTHROPIC_API_KEY', '')
    api_key = st.text_input(
        "API Key",
        value=default_key,
        type="password",
        help="Anthropic API 키를 입력하세요"
    )

    if api_key:
        os.environ['ANTHROPIC_API_KEY'] = api_key
        st.success("✅ API 키 설정 완료")
    else:
        st.warning("⚠️ API 키를 입력해주세요")

    st.markdown("---")
    st.markdown("### 📖 사용 방법")
    st.markdown("""
    1. 왼쪽 폼에 제품 정보 입력
    2. '가격 정책 분석 시작' 버튼 클릭
    3. 4단계 분석이 자동 실행됩니다
    4. 최종 권고안을 확인하세요
    """)

# 메인 컨텐츠: 2열 레이아웃
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 정보 입력")

    with st.form("pricing_form"):
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
            "🚀 가격 정책 분석 시작",
            use_container_width=True,
            type="primary"
        )

with col2:
    st.header("📊 분석 결과")

    if submitted:
        if not api_key:
            st.error("⚠️ API 키를 먼저 입력해주세요 (왼쪽 사이드바)")
        elif not all([product_overview, variable_costs, fixed_costs, usage_pattern,
                      target_customers, business_goals]):
            st.error("⚠️ 모든 필수 항목을 입력해주세요")
        else:
            # 사용자 데이터 구성
            user_data = {
                'product_overview': product_overview,
                'variable_costs': variable_costs,
                'fixed_costs': fixed_costs,
                'usage_pattern': usage_pattern,
                'target_customers': target_customers,
                'business_goals': business_goals,
                'constraints': constraints if constraints else "특별한 제약사항 없음"
            }

            # 진행 상태 표시
            progress_placeholder = st.empty()
            result_placeholder = st.empty()

            try:
                # Agent 실행
                agent = PricingAgent(st.session_state.prompts)

                def update_progress(message):
                    progress_placeholder.info(f"⏳ {message}")

                with st.spinner("분석을 진행하고 있습니다..."):
                    results = agent.run_full_analysis(user_data, update_progress)

                progress_placeholder.success("✅ 분석 완료!")
                st.session_state.results = results

            except Exception as e:
                st.error(f"❌ 오류 발생: {str(e)}")
                with st.expander("상세 오류 정보"):
                    st.code(traceback.format_exc())

# 결과 표시
if st.session_state.results:
    st.markdown("---")
    st.header("📈 최종 분석 결과")

    tabs = st.tabs([
        "🎯 최종 권고안",
        "💵 비용 분석",
        "🔍 시장 조사",
        "💡 가격 모델",
        "📊 재무 시뮬레이션"
    ])

    with tabs[0]:
        st.markdown(st.session_state.results['final_recommendation'])

        # 다운로드 버튼
        full_report = f"""# SaaS 가격 정책 분석 보고서

## 최종 권고안
{st.session_state.results['final_recommendation']}

---

## 상세 분석 결과

### 1. 비용 분석
{st.session_state.results['cost_analysis']}

### 2. 시장 조사
{st.session_state.results['market_research']}

### 3. 가격 모델 설계
{st.session_state.results['pricing_model']}

### 4. 재무 시뮬레이션
{st.session_state.results['financial_simulation']}
"""

        st.download_button(
            label="📥 전체 보고서 다운로드 (Markdown)",
            data=full_report,
            file_name="pricing_analysis_report.md",
            mime="text/markdown"
        )

    with tabs[1]:
        st.markdown("### 비용 분석 결과")
        st.markdown(st.session_state.results['cost_analysis'])

    with tabs[2]:
        st.markdown("### 시장 가격 조사 결과")
        st.markdown(st.session_state.results['market_research'])

    with tabs[3]:
        st.markdown("### 가격 모델 설계")
        st.markdown(st.session_state.results['pricing_model'])

    with tabs[4]:
        st.markdown("### 재무 시뮬레이션")
        st.markdown(st.session_state.results['financial_simulation'])

# 푸터
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Powered by Claude API | SaaS 가격 정책 수립 시스템</div>",
    unsafe_allow_html=True
)
