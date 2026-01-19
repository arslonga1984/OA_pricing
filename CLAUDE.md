# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Korean-language SaaS pricing consulting system built using a multi-agent prompt architecture. The system helps businesses establish data-driven pricing strategies through structured analysis across four specialized domains: cost analysis, market research, pricing model design, and financial simulation.

## Architecture

### Agent System Structure

The project implements a **Main Agent + Skills** pattern:

**Main Agent: 가격 정책 컨설턴트 (Pricing Policy Consultant)**
- Orchestrates the entire pricing analysis workflow
- Collects user requirements and business context
- Sequentially invokes four specialized skills
- Synthesizes results into 2-3 pricing options with recommendations

**Skill 1: 비용 분석기 (Cost Analyzer)**
- Calculates total costs across different user scales (10, 50, 100, 500, 1000 users)
- Determines break-even points and minimum pricing
- Performs cost sensitivity analysis (±30% usage variation)
- Analyzes economies of scale

**Skill 2: 시장 가격 조사기 (Market Price Researcher)**
- Web searches for competitor pricing data
- Benchmarks market pricing models (per-user, usage-based, tiered, hybrid)
- Analyzes market positioning (premium, mid-market, budget)
- Identifies Korean market-specific pricing practices

**Skill 3: 가격 모델 설계기 (Pricing Model Designer)**
- Designs 3-4 pricing tiers based on cost and market data
- Defines feature/limit differentiation per tier
- Implements price anchoring strategies
- Plans upsell/cross-sell opportunities

**Skill 4: 재무 시뮬레이터 (Financial Simulator)**
- Projects 12-month revenue, costs, and profitability
- Calculates key SaaS metrics (MRR, ARR, ARPU, LTV, CAC, LTV/CAC ratio)
- Runs scenario analysis (optimistic, baseline, pessimistic)
- Performs sensitivity analysis on pricing, customer count, churn rate

### Execution Flow

The Main Agent follows a strict 6-stage process:
1. Information Collection - Gathers product details, costs, usage patterns, target customers
2. Cost Analysis - Invokes Skill 1
3. Market Research - Invokes Skill 2
4. Pricing Model Design - Invokes Skill 3
5. Financial Validation - Invokes Skill 4
6. Final Recommendation - Synthesizes all analysis into actionable options

Data flows sequentially: Cost Analysis → Market Research → Pricing Design → Financial Simulation

### Web Application Architecture

The system is implemented as a Streamlit web application with three main components:

**prompts.py - Prompt Loader**
- Uses regex to extract Main Agent and Skill prompts from `saas_pricing_prompts.md`
- Returns a dictionary of prompts keyed by role (main_agent, cost_analyzer, market_researcher, pricing_designer, financial_simulator)

**agent.py - Agent Orchestration**
- `PricingAgent` class manages Claude API calls
- `run_skill()` method executes individual skills with previous results as context
- `run_full_analysis()` orchestrates the complete 4-skill workflow + final recommendation
- Uses Claude Opus 4.5 model (claude-opus-4-5-20251101)
- Progress callbacks allow UI updates during long-running analysis

**app.py - Streamlit UI**
- Two-column layout: Input form (left) and results display (right)
- Session state management for results persistence
- Tabbed interface for viewing individual analysis stages
- Markdown report download functionality
- API key can be set via .env file or sidebar input

## Language & Localization

- All prompts are in Korean
- Currency: Korean Won (₩/KRW) with USD conversion at ₩1,450 per $1
- Market context: Korean B2B SaaS market with local payment customs and VAT practices
- Web search queries include both English and Korean terms

## Key Design Patterns

### Structured Output Format
Each skill produces standardized outputs with:
- Tables for quantitative data
- "핵심 지표" (Key Metrics) sections
- "인사이트" (Insights) bullet points
- "가정 사항" (Assumptions) documentation

### Data-Driven Decision Making
- Every recommendation requires supporting data or market evidence
- Assumptions must be explicitly stated
- Uncertainty is clearly marked and verified with users

### User Interaction Points
- Main Agent asks clarifying questions for missing information
- Users can intervene between skills to adjust assumptions
- Iterative refinement supported for scenario testing

## Cost Structure Calculations

The system expects two cost types:
- **Fixed Costs**: Personnel, infrastructure base fees, office expenses
- **Variable Costs**: LLM API costs, AWS usage, per-usage fees

Calculations performed at 10, 50, 100, 500, 1000 user scales to identify:
- Per-user cost at each scale
- Break-even points at target margin rates
- Cost optimization thresholds

## SaaS Metrics & Benchmarks

Target benchmarks used in financial validation:
- LTV/CAC Ratio: 3:1 or higher
- Payback Period: 12 months or less
- Gross Margin: 70%+
- Monthly Churn Rate: 5% or lower

## Development Commands

### Running the Web Application
```bash
# Install dependencies
pip install -r requirements.txt

# Set up API key (option 1: .env file)
copy .env.example .env
# Then edit .env with your ANTHROPIC_API_KEY

# Run the Streamlit app
streamlit run app.py
```

The app will open at http://localhost:8501

### Testing Individual Components
```python
# Test prompt loader
python -c "from prompts import load_prompts; print(load_prompts().keys())"

# Test agent (requires API key in .env)
python -c "from agent import PricingAgent; from prompts import load_prompts; agent = PricingAgent(load_prompts())"
```

## File Structure

- `saas_pricing_prompts.md` - Complete prompt definitions for Main Agent and all 4 Skills
- `app.py` - Streamlit web application (main entry point)
- `prompts.py` - Prompt loader that extracts prompts from markdown file
- `agent.py` - Claude API integration and agent orchestration logic
- `requirements.txt` - Python dependencies (streamlit, anthropic, python-dotenv)
- `.env.example` - Template for environment variables
- `.gitignore` - Git ignore rules (excludes .env, venv, etc.)

## Extending the System

To add new skills or modify existing ones:
1. Define skill role and objectives
2. Specify input data requirements (from previous skills)
3. Detail analysis tasks to perform
4. Structure output format with tables, metrics, and insights
5. Update Main Agent workflow to invoke new skill
6. Ensure data handoff between sequential skills

## Integration Possibilities

The document mentions potential integrations:
- Google Sheets for real-time data updates
- Slack/Discord for team collaboration
- Automated periodic market price monitoring
- A/B testing results incorporation
