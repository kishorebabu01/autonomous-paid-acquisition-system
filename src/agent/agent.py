# src/agent/agent.py
# Purpose: LangChain AI agent that reads flagged campaigns
# and decides + executes the correct action using Groq

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# ── Setup ──────────────────────────────────────────────
load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ── Initialize Groq LLM ────────────────────────────────
# This is the brain — Groq runs LLaMA 3 at lightning speed
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    api_key=os.getenv("GROQ_API_KEY")
)

# ══════════════════════════════════════════════════════
# THE 4 TOOLS — Actions the agent can take
# ══════════════════════════════════════════════════════

@tool
def pause_adset(adset_id: str) -> str:
    """
    Pause a severely underperforming ad set to stop wasting budget.
    Use this when ROAS is below 1.0 or CPA ratio is above 5x target.
    """
    # In production: would call Meta Ads API to pause the ad set
    # For portfolio: we simulate the action and log it
    result = f"Ad set {adset_id} has been PAUSED via Meta Ads API."
    print(f"  🔴 ACTION: {result}")
    return result


@tool
def shift_budget(from_adset_id: str, to_adset_id: str, amount: float) -> str:
    """
    Shift budget from an underperforming ad set to a better performing one.
    Use this when one ad set has high CPA but another in same campaign has low CPA.
    Amount should be between 10 and 500.
    """
    result = f"Shifted ${amount} budget from {from_adset_id} to {to_adset_id} via Meta Ads API."
    print(f"  💰 ACTION: {result}")
    return result


@tool
def generate_copy(adset_id: str, issue: str) -> str:
    """
    Generate a new ad copy variant for an underperforming ad set.
    Use this when CTR is low but CPA ratio is between 2-4x (not catastrophic).
    Issue should describe what's wrong: 'low CTR', 'ad fatigue', 'poor engagement'.
    """
    # This tool calls Groq again to generate actual ad copy
    copy_prompt = f"""
    You are an expert Facebook/Meta ads copywriter.
    
    Create a new high-converting ad copy for an ad set with this issue: {issue}
    
    Write:
    1. Headline (max 40 characters)
    2. Primary text (max 125 characters) 
    3. Description (max 30 characters)
    
    Make it urgent, benefit-focused, and action-oriented.
    Format as JSON with keys: headline, primary_text, description
    """
    
    response = llm.invoke(copy_prompt)
    copy_text = response.content
    
    result = f"New copy variant generated for {adset_id}: {copy_text}"
    print(f"  ✍️  ACTION: New copy generated for {adset_id}")
    return result


@tool
def flag_for_human(adset_id: str, reason: str) -> str:
    """
    Flag a campaign for human review when situation is complex or unclear.
    Use this when the issue requires strategic judgment beyond automation.
    """
    result = f"Ad set {adset_id} flagged for human review. Reason: {reason}"
    print(f"  👤 ACTION: {result}")
    return result


# ══════════════════════════════════════════════════════
# AGENT SETUP
# ══════════════════════════════════════════════════════

# List of tools the agent can use
tools = [pause_adset, shift_budget, generate_copy, flag_for_human]

# The system prompt — this is the agent's "job description"
# This tells the agent WHO it is and HOW to think
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert paid acquisition AI agent managing Meta Ads campaigns.

Your job is to analyze underperforming ad sets and take the correct action.

DECISION RULES — follow these strictly:

1. PAUSE the ad set if:
   - ROAS is below 1.0 (losing money)
   - CPA ratio is above 5x target
   - Severity is HIGH

2. SHIFT BUDGET if:
   - CPA ratio is between 2x-5x target
   - There are better performing ad sets in the same campaign
   - Severity is MEDIUM-HIGH

3. GENERATE NEW COPY if:
   - CTR dropped more than 50% vs baseline
   - CPA ratio is between 2x-3x (not catastrophic)
   - Likely ad fatigue issue
   - Severity is MEDIUM

4. FLAG FOR HUMAN if:
   - Situation is complex or contradictory
   - Budget implications are large (>$1000)
   - Severity is LOW with unclear cause

Always explain your reasoning clearly.
Always call exactly ONE tool per flagged campaign.
Be decisive — do not hedge or say "it depends"."""),
    
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Create the agent
# Create the agent
agent_executor = create_react_agent(
    llm,
    tools
)


# ══════════════════════════════════════════════════════
# FETCH + PROCESS FLAGGED CAMPAIGNS
# ══════════════════════════════════════════════════════

def fetch_flagged_campaigns():
    """Fetch all unprocessed flagged campaigns from Supabase"""
    response = supabase.table("flagged_campaigns")\
        .select("*")\
        .eq("is_processed", False)\
        .order("anomaly_score", desc=True)\
        .execute()
    
    return response.data


def log_decision(flagged_campaign: dict, action_taken: str, 
                 ai_reasoning: str, copy_variant: str = None,
                 estimated_spend_saved: float = 0.0):
    """Log the agent's decision to agent_decisions table"""
    
    decision = {
        "flagged_campaign_id": flagged_campaign["id"],
        "campaign_id": flagged_campaign["campaign_id"],
        "adset_id": flagged_campaign["adset_id"],
        "adset_name": flagged_campaign["adset_name"],
        "action_taken": action_taken,
        "action_reason": flagged_campaign["flag_reason"],
        "ai_reasoning": ai_reasoning,
        "copy_variant_generated": copy_variant,
        "execution_status": "executed",
        "estimated_spend_saved": estimated_spend_saved,
        "executed_at": datetime.now().isoformat()
    }
    
    supabase.table("agent_decisions").insert(decision).execute()
    print(f"  📝 Decision logged to Supabase")


def mark_as_processed(flagged_id: str):
    """Mark flagged campaign as processed so agent doesn't act on it again"""
    supabase.table("flagged_campaigns")\
        .update({"is_processed": True})\
        .eq("id", flagged_id)\
        .execute()


def process_flagged_campaign(campaign: dict):
    """
    Main function — sends one flagged campaign to the AI agent
    and processes the decision
    """
    print(f"\n{'='*60}")
    print(f"🎯 Processing: {campaign['adset_name']}")
    print(f"📊 Severity: {campaign['flag_severity'].upper()}")
    print(f"⚠️  Reason: {campaign['flag_reason']}")
    print(f"📈 Anomaly Score: {campaign['anomaly_score']}")
    print(f"{'='*60}")

    # Build the input message for the agent
    agent_input = f"""
    Analyze this underperforming Meta Ads ad set and take action:
    
    Ad Set Name: {campaign['adset_name']}
    Ad Set ID: {campaign['adset_id']}
    Campaign ID: {campaign['campaign_id']}
    
    Problem detected:
    - Flag Reason: {campaign['flag_reason']}
    - Severity: {campaign['flag_severity']}
    - CPA Ratio: {campaign['cpa_ratio']} (how many times over target CPA)
    - CTR Drop: {campaign['ctr_drop_pct']}% below 7-day baseline
    - ROAS Trend: {campaign['roas_trend']}
    - Anomaly Score: {campaign['anomaly_score']}
    
    Better performing ad sets in account for budget shifting:
    - adset_004 (Broad 18-45 India) — ROAS 4.58, CPA ratio 0.15
    - adset_003 (Interest Fitness 25-34) — ROAS 3.94, CPA ratio 0.11
    - adset_001 (Lookalike 1% Purchase) — ROAS 5.90, CPA ratio 0.10
    
    Analyze the situation and call the appropriate tool.
    Explain your full reasoning before calling the tool.
    """

    # Run the agent
    result = agent_executor.invoke({
    "messages": [("human", agent_input)]
})
    ai_reasoning = result["messages"][-1].content
    
    
    # Determine action taken from reasoning
    action_taken = "flag_for_human"  # default
    if "pause" in ai_reasoning.lower():
        action_taken = "pause_adset"
        estimated_spend_saved = float(campaign['cpa_ratio']) * 50 * 10
    elif "shift" in ai_reasoning.lower() or "budget" in ai_reasoning.lower():
        action_taken = "shift_budget"
        estimated_spend_saved = float(campaign['cpa_ratio']) * 50 * 5
    elif "copy" in ai_reasoning.lower() or "creative" in ai_reasoning.lower():
        action_taken = "generate_copy"
        estimated_spend_saved = float(campaign['cpa_ratio']) * 50 * 3
    else:
        estimated_spend_saved = 0.0

    # Log decision to Supabase
    log_decision(
        flagged_campaign=campaign,
        action_taken=action_taken,
        ai_reasoning=ai_reasoning,
        estimated_spend_saved=estimated_spend_saved
    )
    
    # Mark as processed
    mark_as_processed(campaign["id"])
    
    print(f"\n✅ Processed: {campaign['adset_name']}")
    print(f"   Action: {action_taken}")
    print(f"   Estimated spend saved: ${estimated_spend_saved:.2f}")


# ══════════════════════════════════════════════════════
# MAIN EXECUTION
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🤖 AI Agent Starting...")
    print("=" * 60)
    
    # Fetch all unprocessed flagged campaigns
    flagged = fetch_flagged_campaigns()
    
    if not flagged:
        print("✅ No flagged campaigns to process. All clear!")
    else:
        print(f"📋 Found {len(flagged)} flagged campaigns to process")
        print("Processing in order of anomaly score (worst first)...\n")
        
        # Process each flagged campaign one by one
        for campaign in flagged:
            process_flagged_campaign(campaign)
        
        print("\n" + "=" * 60)
        print(f"✅ ALL DONE! Processed {len(flagged)} campaigns")
        print("Check agent_decisions table in Supabase for full log")