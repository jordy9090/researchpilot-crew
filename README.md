# ResearchPilot Crew

ResearchPilot Crew is a CrewAI-based multi-agent system that turns an unstructured research or startup idea dump into a structured research brief, experiment plan, MVP validation plan, 48-hour action plan, advisor update message, and execution logs.

The default mode is deterministic mock mode, so the TA can run and inspect the system without an API key.

This repository corresponds to the CrewAI system for the homework. It is independent from the LangGraph-based Re:mind system submitted separately.

## TA Quick Start

Recommended Python version: 3.10 or 3.11.

```bash
pip install -r requirements.txt
python main.py --mode mock --input data/sample_inputs/wsdm_idea.txt
```

This command runs the full 8-agent workflow without any API key and generates:

- `outputs/research_brief.md`
- `outputs/advisor_message.md`
- `outputs/action_plan.json`
- `outputs/agent_outputs.json`
- `outputs/run_log.json`

Optional smoke test:

```bash
python smoke_test.py
```

If the TA wants to inspect an example without running the program first, see `sample_outputs/`.

## Why This Is an Agentic System

ResearchPilot Crew uses 8 specialized agents that collaborate as a research team. The workflow routes the input, chains agent outputs, uses local tools, applies guardrails, reflects through a harsh reviewer, writes outputs to files, and records evaluation logs.

Live mode contains a CrewAI sequential crew. If CrewAI or an API key is unavailable, the system falls back to mock mode rather than crashing.

## API Key Policy

No API keys are included in this repository. `.env` is ignored by git, and `.env.example` contains empty placeholders only.

Mock mode is the recommended reproducible grading path. Live mode optionally reads `OPENAI_API_KEY` from the environment if the TA wants to test with a lab-owned key.

## Agents

| # | Agent | Role | Main Output |
|---|---|---|---|
| 1 | Intake & Triage Agent | Classifies the idea and chooses the route | task type, urgency, constraints, missing info |
| 2 | Research Question Architect | Turns the idea into a research frame | problem, gap, research question, contributions |
| 3 | Literature Scout | Finds related work directions using local paper cards | search queries, seed papers, reading priority |
| 4 | Experiment Designer | Designs datasets, baselines, metrics, and ablations | experiment plan |
| 5 | Startup Validator | Connects the idea to Re:mind or MVP validation | target users, pain points, MVP feature |
| 6 | Execution Planner | Creates a 48-hour plan | today, tomorrow, this week, do-not-do list |
| 7 | Harsh Reviewer | Critiques novelty, feasibility, clarity, and scope | reviewer scores and required revision |
| 8 | Report Writer | Synthesizes final Markdown outputs | research brief and advisor message |

## Agentic Design Patterns

| Pattern | Implementation |
|---|---|
| Multi-agent collaboration | 8 agents divide triage, research framing, literature, experiment design, startup validation, execution, review, and reporting. |
| Prompt chaining | Each stage uses previous structured outputs as context for the next stage. |
| Routing | Intake & Triage Agent routes to `wsdm_paper`, `remind_mvp`, `lab_meeting`, `professor_outreach`, or `general`. |
| Tool use | Local tools include paper search, JSON/Markdown saving, memory load/save, priority scoring, validation, and scope detection. |
| Reflection / critic-reviewer | Harsh Reviewer critiques the plan, and Report Writer incorporates the critique. |
| Memory management | `data/project_memory.json` stores previous run summaries. |
| Guardrails / safety | The runner handles empty input, scope creep, missing dataset, impossible deadlines, and too many TODOs. |
| Exception handling and recovery | Missing API key, CrewAI import failure, saving errors, and invalid JSON-like outputs are handled without crashing. |
| Evaluation and monitoring | `outputs/run_log.json` records mode, timestamp, agents, patterns, warnings, completeness score, TODO count, and fallback status. |

## Setup

From this folder:

```bash
pip install -r requirements.txt
```

If `python` is not on PATH on Windows, use the Python executable installed by your environment or IDE. The source code itself has no hardcoded absolute paths.

Optional live mode:

```bash
copy .env.example .env
```

Then add `OPENAI_API_KEY` and set `USE_STUB=0`. If no key is available, use mock mode.

## CLI Run Instructions

Run the WSDM/Re:mind sample:

```bash
python main.py --mode mock --input data/sample_inputs/wsdm_idea.txt
```

Run with raw text:

```bash
python main.py --mode mock --text "I want to build a WSDM paper from Re:mind long-term memory retrieval."
```

Auto mode uses live mode only when `OPENAI_API_KEY` exists and `USE_STUB` is not `1`. Otherwise it uses deterministic mock mode:

```bash
python main.py --mode auto --input data/sample_inputs/wsdm_idea.txt
```

## Streamlit Run Instructions

```bash
streamlit run app.py
```

The Streamlit UI calls the same backend function as the CLI:

```python
run_research_pilot()
```

There is no duplicated agent logic in the frontend.

## Mock Mode

Mock mode is the reliable grading path. It simulates all 8 agents with deterministic local functions and still uses the same schemas, guardrails, memory, output saving, and run logging.

For the WSDM sample, mock mode produces:

- a selective long-term memory retrieval research question,
- related work directions,
- datasets such as real counselor records, PsychEval, ESConv, and synthetic multi-session data,
- baselines such as no memory, full history, BM25, vector retrieval, and selective retrieval,
- metrics such as evidence precision, faithfulness, completeness, review burden, and safety-boundary violation,
- a 48-hour plan and advisor update.

## Output Files

Each run saves:

| File | Purpose |
|---|---|
| `outputs/research_brief.md` | Polished research-to-action brief |
| `outputs/advisor_message.md` | Short sendable advisor update |
| `outputs/action_plan.json` | Structured today/tomorrow/this-week plan |
| `outputs/agent_outputs.json` | Raw structured output from each agent |
| `outputs/run_log.json` | Monitoring and evaluation log |

## Troubleshooting

- If `OPENAI_API_KEY` is missing, run `python main.py --mode mock ...`.
- If CrewAI installation is slow or unavailable, mock mode still satisfies the runnable demo path.
- If `python` is not recognized, use the Python launcher or interpreter path available in your environment.
- If output files are not visible, check the `Saved files` paths printed by the CLI.
- If input is empty, the system returns a helpful result and writes output files instead of crashing.
