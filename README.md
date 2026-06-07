# World Cup Command Center 2026

A zero-cost, local-first football intelligence platform for the FIFA World Cup 2026.

## Final build included

- 48-team realistic data layer
- Match Predictor
- Full 48-team tournament simulation
- 100,000 Monte Carlo simulation mode
- Real multi-agent intelligence layer
- Mistral Chief Analyst
- Ask the Coach strategic module
- What-if scenarios
- Data Sources page

## Multi-Agent Intelligence Layer

Specialist agents run before the Chief Analyst:

```text
Stats Agent
Scout Agent
Tactical Agent
Player Agent
News Agent
Debate Agent
        ↓
Chief Analyst — Mistral Medium
        ↓
World Cup Executive Briefing
```

The orchestration is implemented locally and is LangGraph/CrewAI/AutoGen-ready through the contract in `frameworks/langgraph_ready_orchestration.py`.

## Run locally

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set MISTRAL_API_KEY=your_key
set MISTRAL_MODEL=mistral-medium-latest
streamlit run app.py
```

Without `MISTRAL_API_KEY`, the app still works with deterministic local analysis.

## Ask the Coach examples

- What is Portugal's most likely path to the final?
- Which team is the biggest dark horse?
- What happens if Mbappé misses the quarter-finals?

## Data strategy

The app uses realistic local caches for FIFA ranking, Elo ratings, historical results and players. SofaScore is optional/cache-first and not required for the demo.
