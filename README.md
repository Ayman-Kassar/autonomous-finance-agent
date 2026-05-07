# Autonomous Finance Agent

A goal-based AI agent that plans its own steps, decides which tools 
to use and in what order, and produces a complete CFO report — 
all from a single high-level goal.

## 🎯 Business Problem
Traditional automation requires you to define every step.
This agent receives a goal and figures out the steps itself —
like giving a task to a senior analyst and letting them run with it.

## 🤖 How It Works

You give it one goal:
"Analyse January performance across all markets. Find the worst 
performing market. Calculate all variances. Prepare a CFO summary."

The agent decides by itself:
- Which markets to fetch data for
- How many variance calculations to run
- What order to do everything in
- When it has enough information to write the report
- When the goal is complete

## 📊 What It Does in 3 Steps

**Step 1** — Fetches financial data for all 5 markets simultaneously

**Step 2** — Calculates revenue and cost variances for each market,
ranks markets by performance, identifies worst performer

**Step 3** — Writes complete CFO report with:
- Executive summary
- Market rankings
- Key findings per market
- Specific recommended actions with owners and deadlines
- Saves report to file automatically

## 💡 Key Insight
You never told it to call calculate_variance 8 times.
You never told it which market was worst.
You never told it what to put in the CFO report.
It figured all of that out from the goal alone.

## 🛠️ Tools
- Claude Sonnet API with tool use (Anthropic)
- Python 3.12
- python-dotenv

## 🚀 How to Run
```bash
git clone https://github.com/Ayman-Kassar/autonomous-finance-agent
cd autonomous-finance-agent
pip install anthropic python-dotenv
cp .env.example .env  # add your ANTHROPIC_API_KEY
python finance_agent.py
```

## 📁 Output
Generates `cfo_report.txt` — a complete formal CFO report
with findings and recommended actions.

## 🔗 Related Projects
For a more advanced version with LangGraph state management,
human approval gates, and persistence — see:
[audit-risk-scanner](https://github.com/Ayman-Kassar/audit-risk-scanner)

## 💼 Portfolio Context
Demonstrates autonomous agent architecture — the most advanced 
pattern in production AI systems today. Shows the progression 
from tool calling to full goal-based autonomy.
Built by a 15+ year FP&A and audit professional who also 
understands the finance domain these tools operate in.
