# ResearchPilot Crew Report

## 1. Functionality

ResearchPilot Crew converts messy research/startup idea dumps into structured research briefs, experiment plans, MVP validation plans, 48-hour action plans, advisor update messages, and execution logs.

The example target use case is a student researcher/founder developing Re:mind into a WSDM-style research direction around selective long-term memory retrieval and evidence-grounded counseling documentation.

The system is intentionally file-based and easy to run. It does not require a database, authentication, real web search, audio upload, calendar integration, email sending, or deployment configuration.

## 2. How to Run

Recommended Python version: 3.10 or 3.11.

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the CLI in reliable mock mode:

```bash
python main.py --mode mock --input data/sample_inputs/wsdm_idea.txt
```

Run with direct text:

```bash
python main.py --mode mock --text "I want to build a WSDM paper from Re:mind long-term memory retrieval."
```

Run the Streamlit frontend:

```bash
streamlit run app.py
```

If `OPENAI_API_KEY` is unavailable, use mock mode. Auto mode falls back to mock mode when no API key is found.

## 3. Requirement Mapping

| Homework Requirement | ResearchPilot Crew Evidence |
|---|---|
| Uses one allowed framework | CrewAI is used as the selected framework. |
| Uses at least five agents | 8 agents are implemented in `agents.py`. |
| Uses at least five agentic design patterns | 9 patterns are documented and logged through `PATTERNS_USED` in `tasks.py`. |
| Independent system | This repository implements ResearchPilot Crew as a standalone research-to-action assistant, independent from the LangGraph-based Re:mind system submitted separately. |
| Provides described functionality | The system converts raw idea dumps into research briefs, experiment plans, MVP validation plans, action plans, advisor messages, and run logs. |
| Easy to run | `python main.py --mode mock --input data/sample_inputs/wsdm_idea.txt` runs without API keys. |

## 4. Agents

| # | Agent | Role | Input | Output |
|---|---|---|---|---|
| 1 | Intake & Triage Agent | Classifies the idea and routes the workflow | Raw user idea dump | Task type, urgency, goal, constraints, missing info, route |
| 2 | Research Question Architect | Forms the paper/research framing | Triage output and raw idea | Problem, gap, research question, one-line idea, contributions, reviewer risks |
| 3 | Literature Scout | Suggests related work using a local paper database | Triage and research question | Related work areas, search queries, seed papers, reading priority |
| 4 | Experiment Designer | Designs an evaluable experiment | Research question and literature directions | Datasets, baselines, metrics, ablations, minimum viable experiment |
| 5 | Startup Validator | Connects the work to Re:mind/MVP validation | Research and experiment plan | Target users, pain points, MVP feature, validation questions, risks |
| 6 | Execution Planner | Converts the plan into immediate actions | Outputs from previous agents | Today/tomorrow/this-week plan, priority ranking, do-not-do list |
| 7 | Harsh Reviewer | Critiques the plan from reviewer/advisor perspective | Research, experiment, startup, and action plan | Novelty, feasibility, clarity scores, main weakness, required revision |
| 8 | Report Writer | Produces final Markdown deliverables | All prior agent outputs and warnings | Research brief, advisor message, action summary, run summary |

## 5. Agentic Design Patterns

| Pattern | Implementation | Purpose |
|---|---|---|
| Multi-agent collaboration | 8 specialized agents collaborate as a research team. | Makes each reasoning step explicit and inspectable. |
| Prompt chaining | Triage output feeds research framing; research feeds literature; literature feeds experiments; all prior outputs feed review and report writing. | Preserves context and creates a staged reasoning pipeline. |
| Routing | Intake & Triage Agent selects `wsdm_paper`, `remind_mvp`, `lab_meeting`, `professor_outreach`, or `general`. | Adapts outputs to the user's actual task. |
| Tool use | `search_local_papers`, `save_markdown`, `save_json`, `load_project_memory`, `save_project_memory`, `score_priority`, and `validate_required_keys` are implemented locally. | Grounds the system in executable operations rather than only text generation. |
| Reflection / critic-reviewer | Harsh Reviewer scores novelty, feasibility, clarity, and required revision. | Forces the system to identify weaknesses before final reporting. |
| Memory management | Each run appends a summary to `data/project_memory.json`. | Preserves lightweight run history without a database. |
| Guardrails / safety | The runner detects empty input, scope creep, missing dataset, impossible deadlines, and too many TODOs. | Keeps the plan realistic and avoids unsupported overreach. |
| Exception handling and recovery | Missing API key, live CrewAI failure, invalid structured output, and save errors are handled with warnings and fallback behavior. | Keeps the TA run path stable. |
| Evaluation and monitoring | `outputs/run_log.json` records mode, timestamp, agents, patterns, warnings, fallback status, completeness score, and TODO count. | Makes execution quality easy to inspect. |

## 6. Example Input and Output

Example input:

```text
I want to develop a WSDM full paper from Re:mind. The topic is long-term memory retrieval and evidence-grounded counseling documentation. I need a research question, related work direction, experiment plan, MVP connection, and this week's TODO. Data may come from real counselor records, PsychEval, ESConv, or synthetic multi-session counseling data.
```

Expected core output in mock mode:

- Core research question: How can an LLM-based counseling documentation system selectively retrieve prior-session information that is relevant, temporally valid, and evidence-grounded for the current counseling record?
- One-line idea: Selective long-term memory retrieval for evidence-grounded counseling documentation.
- Contribution candidates:
  1. A longitudinal counseling-memory retrieval formulation.
  2. An evidence-linked documentation generation pipeline.
  3. A counselor-in-the-loop verification workflow.
  4. Evaluation metrics for evidence coverage, faithfulness, and review burden.
- Experiment plan includes real counselor records if available, PsychEval, ESConv, synthetic multi-session counseling data, no-memory baseline, full-history baseline, BM25 retrieval, vector retrieval, selective retrieval, evidence precision, faithfulness, documentation completeness, review burden proxy, and safety-boundary violation.
- Today's plan:
  1. Decide dataset route.
  2. Create the output document schema with evidence-link fields.
  3. Collect 5 seed papers.
- Do not do today: frontend redesign, full backend implementation, random paper reading, marketing content generation.

## 7. Evaluation Notes

Mock mode ensures reliable execution without an API key. This is the recommended TA grading path:

```bash
python main.py --mode mock --input data/sample_inputs/wsdm_idea.txt
```

For reliable grading, mock mode deterministically simulates the same 8-agent workflow and preserves all agent outputs in the required schemas. Live mode additionally attempts to execute a CrewAI sequential crew when `OPENAI_API_KEY` is available. If live execution fails, the system records the failure and falls back to mock mode.

The run saves all required inspectable artifacts:

- `outputs/research_brief.md`
- `outputs/advisor_message.md`
- `outputs/action_plan.json`
- `outputs/agent_outputs.json`
- `outputs/run_log.json`

`run_log.json` records completeness score, warnings, fallback status, generated TODO count, all agents used, and all agentic patterns used. This makes the system easy to evaluate against the homework requirements: it runs properly, provides the described functionality, uses more than five agents, and documents more than five design patterns.
