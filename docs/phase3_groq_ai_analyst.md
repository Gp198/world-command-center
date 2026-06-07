# Phase 3 — Groq AI Analyst

This phase turns the static/local analyst into a real LLM-powered analyst using Groq.

## What was added

- `llm/groq_client.py` — minimal Groq API client using the OpenAI-compatible chat completions endpoint.
- `llm/prompt_builder.py` — system and user prompt builder.
- `llm/groq_analyst.py` — analyst service used by the orchestrator.
- `agents/orchestrator.py` — now builds structured match context and sends it to Groq.
- `app.py` — upgraded **AI Analyst Chat** page.

## How it works

1. User selects two teams and asks a question.
2. The app runs the prediction engine.
3. The local agents generate stats, scouting, tactical and news/context findings.
4. The orchestrator creates a structured JSON context.
5. Groq receives the question + context.
6. The AI Analyst returns a professional football intelligence answer.
7. The local Chief Analyst remains available as a fallback.

## Configure Groq

PowerShell:

```powershell
$env:GROQ_API_KEY="your_api_key_here"
$env:GROQ_MODEL="llama-3.3-70b-versatile"
streamlit run app.py
```

CMD:

```cmd
set GROQ_API_KEY=your_api_key_here
set GROQ_MODEL=llama-3.3-70b-versatile
streamlit run app.py
```

If you do not set `GROQ_API_KEY`, the application still runs and shows setup instructions inside the AI Analyst page.

## Default model

The default model is:

```text
llama-3.3-70b-versatile
```

You can override it with `GROQ_MODEL`.

## Example question

```text
Why is Portugal favoured against Brazil?
```

The analyst uses:

- win probabilities
- expected goals
- Elo ratings
- FIFA ranking
- form
- attack/defense strength
- squad strength
- knowledge snippets
- deterministic agent findings

## Safety and quality rules

The prompt instructs the model to:

- use only provided data/context;
- avoid certainty;
- distinguish model signal from tactical interpretation;
- not invent player-specific facts when data is missing;
- return a premium markdown response.
