import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# PAGE SETUP
st.set_page_config(page_title="CMO.AI Marketing Agent", layout="wide")
st.title("CMO.AI – Marketing Strategy Agent")

# API KEY
os.environ["GROQ_API_KEY"] = "GROQ_API_KEY"

# LLM 
llm = ChatGroq(
    model_name="openai/gpt-oss-120b",
    temperature=0.4
)

# TOOLS 

def budget_allocator(budget, platforms):
    if not platforms:
        return "No platforms selected"

    allocation = {}
    per_platform = budget / len(platforms)

    for p in platforms:
        allocation[p] = {
            "ads": round(per_platform * 0.7, 2),
            "content": round(per_platform * 0.3, 2)
        }

    return allocation


def platform_strategy(audience):
    audience = audience.lower()

    if "18" in audience or "young" in audience:
        return "Focus on TikTok & Instagram (short-form video, trends, influencers)."
    elif "professional" in audience:
        return "Focus on LinkedIn & YouTube (educational + authority content)."
    else:
        return "Balanced mix of Instagram, Facebook, and YouTube."


def financial_model(budget):
    """
    REAL calculations (not LLM guessing)
    """
    ctr = 0.02
    conversion_rate = 0.03
    avg_order_value = 30

    clicks = int(budget / 0.5)  # assume $0.5 CPC
    sales = int(clicks * conversion_rate)
    revenue = sales * avg_order_value

    cpa = budget / sales if sales > 0 else 0
    roas = revenue / budget if budget > 0 else 0

    return {
        "Estimated Clicks": clicks,
        "Estimated Sales": sales,
        "Estimated Revenue": revenue,
        "CPA": round(cpa, 2),
        "ROAS": round(roas, 2)
    }


def decision_logic(budget):
    if budget < 500:
        return "Low budget → Focus on organic content + 1 platform only. Avoid paid ads."
    elif budget < 1500:
        return "Medium budget → Mix organic + small paid ads + micro-influencers."
    else:
        return "High budget → Scale paid ads, influencers, and content production."


def competitor_insight(industry):
    return f"In the {industry} industry, many competitors focus on generic messaging. A strong opportunity is to differentiate through authenticity, niche targeting, and community-driven branding."

# USER FORM 
with st.form("marketing_form"):

    st.header("Business Information")

    col1, col2 = st.columns(2)

    with col1:
        brand = st.text_input("Brand Name")
        industry = st.text_input("Industry")
        product = st.text_input("Product / Service")

    with col2:
        audience = st.text_input("Target Audience")
        budget = st.number_input("Marketing Budget ($)", min_value=0)
        goal = st.selectbox(
            "Main Goal",
            ["Brand Awareness", "Increase Sales", "Lead Generation"]
        )

    platforms = st.multiselect(
        "Marketing Platforms",
        ["Instagram", "TikTok", "YouTube", "Facebook", "LinkedIn"]
    )

    submitted = st.form_submit_button("Generate Marketing Strategy")

# PROMPT
template = """
You are a senior Chief Marketing Officer (CMO).

Use ALL the structured insights below to create a REALISTIC, data-driven marketing strategy.

BUSINESS:
Brand: {brand}
Industry: {industry}
Product: {product}
Audience: {audience}
Goal: {goal}

PLATFORM INSIGHT:
{platform_insight}

DECISION STRATEGY:
{decision}

COMPETITOR INSIGHT:
{competitor}

BUDGET BREAKDOWN:
{budget_plan}

FINANCIAL PROJECTIONS:
{financials}

Instructions:
- Think step-by-step
- Justify decisions using the numbers
- Be realistic (not overly optimistic)

Generate:

1. Target Audience Analysis
2. Positioning & Differentiation
3. Content Strategy
4. Campaign Plan
5. Weekly Posting Schedule
6. Budget Justification (BASED ON NUMBERS)
7. Expected Results & KPIs (USE financial projections)

Be professional and specific.
"""

prompt = ChatPromptTemplate.from_template(template)

# EXECUTION 
if submitted:

    with st.spinner("Generating marketing strategy..."):

        budget_plan = budget_allocator(budget, platforms)
        platform_insight = platform_strategy(audience)
        financials = financial_model(budget)
        decision = decision_logic(budget)
        competitor = competitor_insight(industry)

        chain = prompt | llm

        response = chain.invoke({
            "brand": brand,
            "industry": industry,
            "product": product,
            "audience": audience,
            "goal": goal,
            "platform_insight": platform_insight,
            "budget_plan": budget_plan,
            "financials": financials,
            "decision": decision,
            "competitor": competitor
        })

        st.success("Marketing Strategy Generated")

        #  OUTPUT 
        st.markdown("##  Financial Model")
        #st.json(financials)

        st.markdown("##  Budget Allocation")
        #st.json(budget_plan)

        st.markdown("##  Strategy Decision")
        #st.info(decision)

        st.markdown("##  Competitor Insight")
        #st.info(competitor)

        st.markdown("##  Marketing Strategy")
        st.write(response.content)