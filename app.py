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
    st.markdown("### 📖 입력 가이드")
    st.markdown("""
    - 🔴 **필수**: 반드시 입력해야 분석 가능
    - 🟡 **선택**: 입력하면 더 정확한 분석
    - 미입력 시 기본값 또는 추정치 사용
    """)

# 메인 컨텐츠: 2열 레이아웃
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 정보 입력")

    with st.form("pricing_form"):
        # ==========================================
        # 섹션 1: 제품/서비스 기본 정보 (필수)
        # ==========================================
        st.subheader("1. 제품/서비스 기본 정보 🔴 필수")

        col_a, col_b = st.columns(2)
        with col_a:
            product_name = st.text_input(
                "제품명 *",
                placeholder="New AI",
                help="제품 또는 서비스의 이름"
            )

        with col_b:
            product_type = st.multiselect(
                "제품 유형 * (복수 선택 가능)",
                options=[
                    "AI 업무 어시스턴트",
                    "AI 챗봇/상담",
                    "문서 자동화",
                    "데이터 분석 도구",
                    "협업/생산성 도구",
                    "마케팅 자동화",
                    "고객 서비스 도구",
                    "기타"
                ],
                default=["AI 업무 어시스턴트"],
                help="제품의 주요 카테고리 (복수 선택 가능)"
            )

        product_description = st.text_area(
            "제품 설명 *",
            placeholder="예: AI 기반 업무 자동화 도구로, 직원들의 반복적인 문서 작업을 자동화하고 생산성을 향상시킵니다. 문서 요약, 검색, 자동 응답 기능을 제공합니다.",
            height=80,
            help="제품이 무엇이고, 어떤 문제를 해결하는지 설명"
        )

        key_features = st.text_area(
            "핵심 기능 (쉼표로 구분) *",
            placeholder="예: 문서 요약, 지능형 검색, 자동 응답, 업무 자동화, 팀 협업",
            height=60,
            help="제품의 주요 기능들"
        )

        st.markdown("---")

        # ==========================================
        # 섹션 2: 비용 구조 (필수)
        # ==========================================
        st.subheader("2. 비용 구조 🔴 필수")

        st.markdown("##### 변동비용 (사용량에 비례)")

        col_c, col_d = st.columns(2)
        with col_c:
            llm_provider = st.selectbox(
                "LLM 제공사 *",
                options=[
                    "OpenAI (GPT-4)",
                    "OpenAI (GPT-4o)",
                    "OpenAI (GPT-3.5)",
                    "Anthropic (Claude)",
                    "Google (Gemini)",
                    "자체 모델",
                    "기타/혼합"
                ],
                help="사용하는 LLM API 제공사"
            )

        with col_d:
            llm_cost_per_user = st.number_input(
                "LLM API 비용 (1인/월, 원) *",
                min_value=0,
                value=5000,
                step=500,
                help="사용자 1인당 월 평균 LLM API 비용 (원화)"
            )

        col_e, col_f = st.columns(2)
        with col_e:
            cloud_provider = st.selectbox(
                "클라우드 제공사",
                options=["AWS", "GCP", "Azure", "NCP (네이버)", "기타"],
                help="사용하는 클라우드 서비스"
            )

        with col_f:
            cloud_cost_per_user = st.number_input(
                "클라우드 비용 (1인/월, 원)",
                min_value=0,
                value=2000,
                step=500,
                help="사용자 1인당 월 평균 클라우드 비용"
            )

        other_variable_cost = st.number_input(
            "기타 변동비 (1인/월, 원)",
            min_value=0,
            value=0,
            step=500,
            help="기타 사용량 비례 비용 (외부 API, 스토리지 등)"
        )

        total_variable = llm_cost_per_user + cloud_cost_per_user + other_variable_cost
        st.info(f"📊 **총 변동비**: ₩{total_variable:,}/인/월")

        st.markdown("##### 고정비용 (사용자 수와 무관)")

        col_g, col_h = st.columns(2)
        with col_g:
            dev_team_size = st.number_input(
                "개발팀 인원 수 *",
                min_value=1,
                value=3,
                step=1,
                help="개발/운영에 참여하는 인원 수"
            )

        with col_h:
            avg_salary = st.number_input(
                "평균 인건비 (1인/월, 만원) *",
                min_value=0,
                value=600,
                step=50,
                help="개발팀 1인당 월 평균 인건비 (만원)"
            )

        col_i, col_j = st.columns(2)
        with col_i:
            infra_base_cost = st.number_input(
                "인프라 기본료 (월, 만원)",
                min_value=0,
                value=50,
                step=10,
                help="서버, 도메인, 보안 등 기본 비용"
            )

        with col_j:
            other_fixed_cost = st.number_input(
                "기타 고정비 (월, 만원)",
                min_value=0,
                value=50,
                step=10,
                help="사무실, 소프트웨어 라이선스 등"
            )

        direct_fixed_cost = st.number_input(
            "직접 입력 고정비 (월, 만원)",
            min_value=0,
            value=0,
            step=10,
            help="고정비용이 없거나 예측하기 어려운 경우 직접 입력"
        )

        total_fixed = (dev_team_size * avg_salary) + infra_base_cost + other_fixed_cost + direct_fixed_cost
        st.info(f"📊 **총 고정비**: ₩{total_fixed * 10000:,}/월 (₩{total_fixed}만원)")

        st.markdown("---")

        # ==========================================
        # 섹션 3: 타겟 고객 (필수)
        # ==========================================
        st.subheader("3. 타겟 고객 🔴 필수")

        col_k, col_l = st.columns(2)
        with col_k:
            business_model = st.selectbox(
                "비즈니스 모델 *",
                options=["B2B (기업 대상)", "B2C (개인 대상)", "B2B + B2C (혼합)"],
                help="주요 고객 유형"
            )

        with col_l:
            target_company_size = st.multiselect(
                "타겟 기업 규모 *",
                options=[
                    "50인 이하",
                    "50-99인",
                    "100-199인",
                    "200-299인",
                    "300-499인",
                    "500~1000인",
                    "1000인 이상"
                ],
                default=["100-199인", "200-299인"],
                help="주요 타겟 기업 규모 (복수 선택 가능)"
            )

        target_industries = st.multiselect(
            "타겟 업종 *",
            options=[
                "IT/소프트웨어",
                "금융/보험",
                "제조업",
                "유통/물류",
                "의료/헬스케어",
                "교육",
                "공공기관",
                "전문서비스 (컨설팅, 법률 등)",
                "미디어/엔터테인먼트",
                "기타/전체 업종"
            ],
            default=["IT/소프트웨어", "금융/보험"],
            help="주요 타겟 업종 (복수 선택 가능)"
        )

        st.markdown("---")

        # ==========================================
        # 섹션 4: 예상 사용 패턴 (선택)
        # ==========================================
        st.subheader("4. 예상 사용 패턴 🟡 선택")

        col_m, col_n = st.columns(2)
        with col_m:
            avg_queries_per_user = st.number_input(
                "평균 쿼리 수 (1인/월)",
                min_value=0,
                value=500,
                step=100,
                help="일반 사용자의 월 평균 쿼리/요청 수"
            )

        with col_n:
            power_user_queries = st.number_input(
                "파워유저 쿼리 수 (1인/월)",
                min_value=0,
                value=2000,
                step=100,
                help="헤비 사용자의 월 쿼리/요청 수"
            )

        usage_variance = st.select_slider(
            "사용량 변동성",
            options=["매우 낮음", "낮음", "보통", "높음", "매우 높음"],
            value="보통",
            help="사용자 간, 월별 사용량 편차 정도"
        )

        st.markdown("---")

        # ==========================================
        # 섹션 5: 사업 목표 (선택)
        # ==========================================
        st.subheader("5. 사업 목표 🟡 선택")

        col_o, col_p = st.columns(2)
        with col_o:
            business_priority = st.selectbox(
                "사업 우선순위",
                options=[
                    "시장점유율 우선 (저가 전략)",
                    "수익성 우선 (고가 전략)",
                    "균형 (중가 전략)"
                ],
                index=2,
                help="초기 사업 전략 방향"
            )

        with col_p:
            target_customers_12m = st.number_input(
                "12개월 목표 고객사 수",
                min_value=0,
                value=50,
                step=10,
                help="12개월 내 유치 목표 고객사 수"
            )

        col_q, col_r = st.columns(2)
        with col_q:
            target_margin = st.slider(
                "목표 마진율 (%)",
                min_value=0,
                max_value=90,
                value=50,
                step=5,
                help="목표 영업이익률"
            )

        with col_r:
            expected_churn = st.slider(
                "예상 월 이탈률 (%)",
                min_value=0.0,
                max_value=20.0,
                value=5.0,
                step=0.5,
                help="월 평균 고객 이탈률"
            )

        st.markdown("---")

        # ==========================================
        # 섹션 6: 경쟁사 및 시장 정보 (선택)
        # ==========================================
        st.subheader("6. 경쟁사 및 시장 정보 🟡 선택")

        main_competitors = st.multiselect(
            "주요 경쟁사",
            options=[
                "ChatGPT Business/Enterprise",
                "Wrks.ai",
                "Microsoft Copilot",
                "Google Duet AI",
                "Notion AI",
                "기타 국내 솔루션",
                "기타 해외 솔루션",
                "직접 입력"
            ],
            default=[],
            help="직접적으로 경쟁하는 제품들"
        )

        competitor_price_info = st.text_area(
            "경쟁사 가격 정보 (알고 있다면)",
            placeholder="ChatGTP Business: $30/월",
            height=60,
            help="알고 있는 경쟁사 가격 정보"
        )

        market_position = st.selectbox(
            "목표 시장 포지션",
            options=[
                "Premium (고가/고기능)",
                "Mid-market (중가/표준기능)",
                "Budget (저가/기본기능)",
                "가격 경쟁력 우선"
            ],
            index=3,
            help="시장에서의 목표 포지션"
        )

        st.markdown("---")

        # ==========================================
        # 섹션 7: 가격 모델 선호도 (선택)
        # ==========================================
        st.subheader("7. 가격 모델 선호도 🟡 선택")

        col_s, col_t = st.columns(2)
        with col_s:
            preferred_pricing_model = st.selectbox(
                "선호 가격 모델",
                options=[
                    "미정 (분석 후 결정)",
                    "정액제 (Per-user)",
                    "종량제 (Usage-based)",
                    "하이브리드 (정액+종량)",
                    "Tiered (단계별 요금제)"
                ],
                index=0,
                help="선호하는 가격 책정 방식"
            )

        with col_t:
            billing_cycle = st.selectbox(
                "선호 결제 주기",
                options=[
                    "월간 결제",
                    "연간 결제",
                    "월간 + 연간 (할인)"
                ],
                index=2,
                help="선호하는 결제 주기"
            )

        freemium_interest = st.selectbox(
            "무료/할인 플랜 제공 의향",
            options=[
                "무료 플랜 없음",
                "기능 제한 무료 플랜",
                "기간 제한 무료 체험",
                "미정"
            ],
            index=2,
            help="무료 플랜 또는 체험 제공 여부"
        )

        st.markdown("---")

        # ==========================================
        # 섹션 8: 기타 제약사항 (선택)
        # ==========================================
        st.subheader("8. 기타 제약사항 🟡 선택")

        other_constraints = st.text_area(
            "추가 고려사항 또는 제약사항",
            placeholder="예: 특정 가격대 이하 유지 필요, 기존 고객 할인 정책 필요, 파트너 리셀러 마진 고려 등",
            height=80,
            help="기타 가격 정책에 영향을 미치는 요소"
        )

        st.markdown("---")

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
        elif not all([product_name, product_type, product_description, key_features]):
            st.error("⚠️ 제품 기본 정보를 모두 입력해주세요")
        elif not target_company_size or not target_industries:
            st.error("⚠️ 타겟 고객 정보를 선택해주세요")
        else:
            # 사용자 데이터 구성 (상세 정보)
            user_data = {
                # 제품 정보
                'product_overview': f"""
제품명: {product_name}
제품 유형: {', '.join(product_type)}
제품 설명: {product_description}
핵심 기능: {key_features}
""",
                # 비용 구조
                'variable_costs': f"""
[변동비용 - 사용자 1인당 월 비용]
- LLM 제공사: {llm_provider}
- LLM API 비용: ₩{llm_cost_per_user:,}/인/월
- 클라우드 ({cloud_provider}): ₩{cloud_cost_per_user:,}/인/월
- 기타 변동비: ₩{other_variable_cost:,}/인/월
- **총 변동비: ₩{total_variable:,}/인/월**
""",
                'fixed_costs': f"""
[고정비용 - 월간]
- 개발팀: {dev_team_size}명 × ₩{avg_salary}만원 = ₩{dev_team_size * avg_salary}만원/월
- 인프라 기본료: ₩{infra_base_cost}만원/월
- 기타 고정비: ₩{other_fixed_cost}만원/월
- 직접 입력 고정비: ₩{direct_fixed_cost}만원/월
- **총 고정비: ₩{total_fixed}만원/월 (₩{total_fixed * 10000:,})**
""",
                # 사용 패턴
                'usage_pattern': f"""
- 평균 사용자 쿼리: {avg_queries_per_user}회/월
- 파워유저 쿼리: {power_user_queries}회/월
- 사용량 변동성: {usage_variance}
""",
                # 타겟 고객
                'target_customers': f"""
- 비즈니스 모델: {business_model}
- 타겟 기업 규모: {', '.join(target_company_size)}
- 타겟 업종: {', '.join(target_industries)}
""",
                # 사업 목표
                'business_goals': f"""
- 사업 우선순위: {business_priority}
- 12개월 목표 고객사: {target_customers_12m}개
- 목표 마진율: {target_margin}%
- 예상 월 이탈률: {expected_churn}%
""",
                # 경쟁사 정보
                'competitor_info': f"""
- 주요 경쟁사: {', '.join(main_competitors) if main_competitors else '미입력'}
- 경쟁사 가격 정보: {competitor_price_info if competitor_price_info else '미입력'}
- 목표 시장 포지션: {market_position}
""",
                # 가격 모델 선호
                'pricing_preferences': f"""
- 선호 가격 모델: {preferred_pricing_model}
- 선호 결제 주기: {billing_cycle}
- 무료 플랜: {freemium_interest}
""",
                # 제약사항
                'constraints': other_constraints if other_constraints else "특별한 제약사항 없음"
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
