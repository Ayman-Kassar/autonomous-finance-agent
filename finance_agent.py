import anthropic
import json
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic()

# ── TOOLS ──────────────────────────────────────────
tools = [
    {
        "name": "get_financial_data",
        "description": "Gets actual vs budget financial data for a market and month. Use when you need financial performance data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "market": {"type": "string", "description": "Market name e.g. Sweden, Germany"},
                "month": {"type": "string", "description": "Month e.g. January, February"}
            },
            "required": ["market", "month"]
        }
    },
    {
        "name": "calculate_variance",
        "description": "Calculates variance between actual and budget. Use when you need variance amounts or percentages.",
        "input_schema": {
            "type": "object",
            "properties": {
                "actual": {"type": "number"},
                "budget": {"type": "number"},
                "metric_name": {"type": "string", "description": "What is being measured e.g. Revenue, Costs"}
            },
            "required": ["actual", "budget", "metric_name"]
        }
    },
    {
        "name": "get_market_ranking",
        "description": "Ranks all markets by a specific metric. Use when asked about best/worst performing markets.",
        "input_schema": {
            "type": "object",
            "properties": {
                "metric": {"type": "string", "description": "Metric to rank by e.g. revenue_variance, profit"}
            },
            "required": ["metric"]
        }
    },
    {
        "name": "save_cfo_report",
        "description": "Saves the final CFO report to a file. Use this as the LAST step when the analysis is complete.",
        "input_schema": {
            "type": "object",
            "properties": {
                "report_title": {"type": "string"},
                "executive_summary": {"type": "string"},
                "key_findings": {"type": "array", "items": {"type": "string"}},
                "recommended_actions": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["report_title", "executive_summary", "key_findings", "recommended_actions"]
        }
    }
]

# ── TOOL FUNCTIONS ──────────────────────────────────
def get_financial_data(market, month):
    data = {
        "Sweden":  {"January": {"revenue_actual": 4200000, "revenue_budget": 4500000, "costs_actual": 3100000, "costs_budget": 2900000}},
        "Germany": {"January": {"revenue_actual": 6800000, "revenue_budget": 7200000, "costs_actual": 4900000, "costs_budget": 4600000}},
        "France":  {"January": {"revenue_actual": 3900000, "revenue_budget": 4100000, "costs_actual": 2800000, "costs_budget": 2700000}},
        "UK":      {"January": {"revenue_actual": 5100000, "revenue_budget": 5400000, "costs_actual": 3600000, "costs_budget": 3400000}},
        "Norway":  {"January": {"revenue_actual": 2800000, "revenue_budget": 2900000, "costs_actual": 2100000, "costs_budget": 2000000}},
    }
    if market in data and month in data[market]:
        return data[market][month]
    return {"error": f"No data for {market} {month}"}

def calculate_variance(actual, budget, metric_name):
    absolute = actual - budget
    percentage = ((actual - budget) / budget) * 100
    return {
        "metric": metric_name,
        "actual": actual,
        "budget": budget,
        "absolute_variance": round(absolute, 2),
        "percentage_variance": round(percentage, 2),
        "status": "favourable" if absolute > 0 else "adverse"
    }

def get_market_ranking(metric):
    markets = ["Sweden", "Germany", "France", "UK", "Norway"]
    results = []
    for market in markets:
        data = get_financial_data(market, "January")
        if "error" not in data:
            rev_var = data["revenue_actual"] - data["revenue_budget"]
            results.append({
                "market": market,
                "revenue_variance": rev_var,
                "revenue_variance_pct": round((rev_var / data["revenue_budget"]) * 100, 2)
            })
    results.sort(key=lambda x: x["revenue_variance"])
    return {"ranking": results, "worst": results[0]["market"], "best": results[-1]["market"]}

def save_cfo_report(report_title, executive_summary, key_findings, recommended_actions):
    report = f"""
{'='*60}
{report_title}
Generated: January 2026
{'='*60}

EXECUTIVE SUMMARY
{executive_summary}

KEY FINDINGS
{chr(10).join([f"• {f}" for f in key_findings])}

RECOMMENDED ACTIONS
{chr(10).join([f"{i+1}. {a}" for i, a in enumerate(recommended_actions)])}

{'='*60}
"""
    with open("cfo_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    return {"status": "Report saved to cfo_report.txt"}

# ── RUN TOOL ───────────────────────────────────────
def run_tool(name, inputs):
    print(f"\n  🔧 Tool: {name}")
    print(f"  📥 {json.dumps(inputs)}")
    if name == "get_financial_data":
        result = get_financial_data(**inputs)
    elif name == "calculate_variance":
        result = calculate_variance(**inputs)
    elif name == "get_market_ranking":
        result = get_market_ranking(**inputs)
    elif name == "save_cfo_report":
        result = save_cfo_report(**inputs)
    else:
        result = {"error": "Unknown tool"}
    print(f"  ✅ Done")
    return result

# ── AGENT LOOP ─────────────────────────────────────
def run_agent(goal):
    print("=" * 60)
    print(f"GOAL: {goal}")
    print("=" * 60)

    messages = [{"role": "user", "content": goal}]
    step = 0

    system = """You are an autonomous finance agent for a manufacturing company.
Your job is to complete financial analysis goals independently.
Use tools to gather data, calculate variances, rank markets.
Always save a final CFO report using save_cfo_report as your last action.
Be thorough but efficient — use only the tools you need."""

    while True:
        step += 1
        print(f"\n--- Agent Step {step} ---")

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            tools=tools,
            system=system,
            messages=messages
        )

        # Agent finished
        if response.stop_reason == "end_turn":
            print("\n✅ Agent completed the goal")
            break

        # Agent wants to use tools
        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        # Safety limit
        if step > 15:
            print("⚠️ Step limit reached")
            break

    print(f"\n📊 Agent completed in {step} steps")

# ── RUN ────────────────────────────────────────────
run_agent(
    "Analyse January performance across all markets. "
    "Find the worst performing market. "
    "Calculate all variances. "
    "Prepare a CFO summary report with key findings and recommended actions."
)