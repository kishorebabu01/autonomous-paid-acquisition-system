# 🤖 Autonomous Paid Acquisition Intelligence System

> AI-powered system that monitors Meta Ads campaigns 24/7, detects anomalies, and autonomously executes optimization actions using LangChain + Groq + Supabase.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![LangChain](https://img.shields.io/badge/LangChain-Latest-green)
![Groq](https://img.shields.io/badge/Groq-LLaMA3.3-orange)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-darkgreen)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-blue)

---

## 🎯 What This System Does

Every 6 hours, this system automatically:

1. **Pulls** campaign performance data from Meta Ads API
2. **Transforms** raw data into marketing KPIs (CTR, CPA, ROAS trends)
3. **Detects** anomalies using SQL-based statistical analysis
4. **Decides** the correct action using an AI agent (LangChain + Groq)
5. **Executes** the action — pause, shift budget, generate copy, or escalate
6. **Logs** every decision with full AI reasoning to Supabase

---

## 🏗️ System Architecture

GitHub Actions (every 6 hours)
↓
Meta Ads API (sandbox) → raw_campaigns table
↓
SQL Transformation → campaign_metrics_view
↓
Anomaly Detection SQL → flagged_campaigns table
↓
LangChain Agent (Groq LLaMA 3.3) → decides action
↓
Tool execution → pause / shift budget / new copy / escalate
↓
agent_decisions table → Looker Studio Dashboard

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| AI Agent Framework | LangChain + LangGraph |
| LLM | Groq (LLaMA 3.3 70B) |
| Database | Supabase (PostgreSQL) |
| Data Transformation | SQL Views + CTEs |
| Anomaly Detection | SQL Statistical Analysis |
| Automation | GitHub Actions (cron) |
| Dashboard | Looker Studio |
| Ad Platform | Meta Ads API (Sandbox) |

---

## 🤖 AI Agent Decision Logic

The LangChain agent receives flagged campaign data and chooses from 4 tools:

| Tool | When Used | Example |
|---|---|---|
| `pause_adset` | ROAS < 1.0 or CPA > 5x target | Retargeting cart abandon ROAS 0.32 |
| `shift_budget` | CPA 2-5x target, better ad sets exist | Move $100 to ROAS 5.90 winner |
| `generate_copy` | CTR dropped >50%, ad fatigue | Refresh creative for low CTR |
| `flag_for_human` | Complex or contradictory signals | Strategic budget decisions |

---

## 📊 Database Schema

```sql
raw_campaigns      -- Raw Meta Ads data (impressions, clicks, spend, ROAS)
campaign_metrics   -- Calculated KPIs (CTR, CPA, trends)
flagged_campaigns  -- Anomaly-detected problem campaigns
agent_decisions    -- AI agent decisions with full reasoning log
```

---

## 🚀 Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/kishorebabu01/autonomous-paid-acquisition-system.git
cd autonomous-paid-acquisition-system
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

### 5. Run the system
```bash
# Generate mock data
python src/data/mock_data_generator.py

# Run AI agent
python src/agent/agent.py
```

---

## 📁 Project Structure

autonomous-paid-acquisition-system/
│
├── src/
│   ├── data/
│   │   ├── mock_data_generator.py    # Generates realistic campaign data
│   │   └── metrics_calculator.py     # Python metrics backup
│   ├── agent/
│   │   └── agent.py                  # LangChain AI agent + 4 tools
│   └── models/
│       └── anomaly_detector.py       # IsolationForest model
│
├── .github/
│   └── workflows/
│       └── run_agent.yml             # GitHub Actions cron job
│
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

---

## 💡 Key Results

- **5 campaigns** analyzed and actioned autonomously
- **$8,222** estimated wasted spend prevented
- **2 ad sets** paused (ROAS below 1.0)
- **2 budget shifts** executed to top performer (ROAS 5.90)
- **1 copy variant** generated for ad fatigue recovery
- **Full audit trail** in Supabase with AI reasoning visible

---

## 🎓 Portfolio Context

This is Project 2 of 10 in my AI Growth Marketing portfolio, built to demonstrate production-grade marketing automation skills for growth roles at FAANG and well-funded startups.

**Project 1:** [AI-Powered Real-Time Personalisation Engine](https://github.com/kishorebabu01)

---

## 📧 Contact

**Kishore** — Growth Marketing + AI Systems
- GitHub: [@kishorebabu01](https://github.com/kishorebabu01)
- LinkedIn: [Add your LinkedIn URL]
