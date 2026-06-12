from __future__ import annotations

from textwrap import shorten
from typing import Any

from tools import score_priority, search_local_papers


def infer_task_type(user_input: str, requested_task_type: str = "auto") -> str:
    if requested_task_type != "auto":
        return requested_task_type
    lowered = user_input.lower()
    if "professor" in lowered or "outreach" in lowered:
        return "professor_outreach"
    if "lab meeting" in lowered or "lab-meeting" in lowered:
        return "lab_meeting"
    if "wsdm" in lowered or "full paper" in lowered or (
        "long-term memory" in lowered and "counseling" in lowered
    ):
        return "wsdm_paper"
    if "re:mind" in lowered or "remind" in lowered or "mvp" in lowered:
        return "remind_mvp"
    return "general"


def run_mock_agents(user_input: str, requested_task_type: str = "auto") -> dict[str, Any]:
    triage = intake_triage(user_input, requested_task_type)
    research = research_question_architect(user_input, triage)
    literature = literature_scout(user_input, triage, research)
    experiment = experiment_designer(user_input, triage, research)
    startup = startup_validator(user_input, triage, research)
    action_plan = execution_planner(user_input, triage, research, experiment, startup)
    review = harsh_reviewer(user_input, triage, research, experiment, startup, action_plan)
    return {
        "Intake & Triage Agent": triage,
        "Research Question Architect": research,
        "Literature Scout": literature,
        "Experiment Designer": experiment,
        "Startup Validator": startup,
        "Execution Planner": action_plan,
        "Harsh Reviewer": review,
    }


def intake_triage(user_input: str, requested_task_type: str = "auto") -> dict[str, Any]:
    task_type = infer_task_type(user_input, requested_task_type)
    lowered = user_input.lower()
    urgency = "high" if any(word in lowered for word in ["today", "48-hour", "this week", "deadline"]) else "medium"

    if task_type == "wsdm_paper":
        main_goal = "Shape a WSDM-style research direction from Re:mind into an experiment-ready paper plan."
        route = "wsdm_paper -> research question -> literature -> experiment -> MVP link -> 48-hour plan"
        constraints = [
            "Must remain evidence-grounded and counseling-domain appropriate.",
            "Needs a dataset decision before serious experiment claims.",
            "Should avoid building a large product before proving the research contribution.",
        ]
    elif task_type == "remind_mvp":
        main_goal = "Choose the next Re:mind MVP feature and validation plan for counselor documentation workflow."
        route = "remind_mvp -> user pain -> feature hypothesis -> validation questions -> build plan"
        constraints = [
            "No database, authentication, audio upload, or production deployment for the MVP decision.",
            "Validation should use lightweight counselor-facing artifacts.",
        ]
    elif task_type == "professor_outreach":
        main_goal = "Turn the research profile into professor outreach angles and meeting preparation tasks."
        route = "professor_outreach -> fit thesis -> email angle -> evidence packet -> meeting TODOs"
        constraints = [
            "Keep outreach specific to each professor's research fit.",
            "Avoid overclaiming unpublished system results.",
        ]
    elif task_type == "lab_meeting":
        main_goal = "Prepare a clear lab-meeting update with research direction, blockers, and next experiments."
        route = "lab_meeting -> status brief -> critique -> next experiment -> advisor questions"
        constraints = ["Prefer crisp research decisions over broad brainstorming."]
    else:
        main_goal = "Convert a messy research/startup idea into a prioritized execution plan."
        route = "general -> clarify goal -> plan research -> plan validation -> next actions"
        constraints = ["Keep the plan small enough to execute in 48 hours."]

    missing_info = []
    if task_type == "wsdm_paper" and not any(word in lowered for word in ["dataset", "data", "psycheval", "esconv", "records"]):
        missing_info.append("Dataset route is not specified.")
    if "metric" not in lowered and task_type in {"wsdm_paper", "general"}:
        missing_info.append("Evaluation metrics need to be selected.")
    if task_type == "professor_outreach" and "professor" in lowered and "name" not in lowered:
        missing_info.append("Target professor names and papers are not listed.")

    return {
        "task_type": task_type,
        "urgency": urgency,
        "main_goal": main_goal,
        "constraints": constraints,
        "missing_info": missing_info,
        "recommended_route": route,
    }


def research_question_architect(user_input: str, triage: dict[str, Any]) -> dict[str, Any]:
    task_type = triage["task_type"]
    if task_type == "wsdm_paper":
        return {
            "problem": (
                "Counseling documentation often requires connecting the current session to prior goals, symptoms, "
                "interventions, homework, and risk signals. Full-history prompting is costly and noisy, while "
                "no-memory generation misses longitudinal context."
            ),
            "gap": (
                "Existing single-turn mental-health QA and generic RAG systems do not directly address longitudinal "
                "evidence selection for counseling documentation."
            ),
            "core_research_question": (
                "How can an LLM-based counseling documentation system selectively retrieve prior-session information "
                "that is relevant, temporally valid, and evidence-grounded for the current counseling record?"
            ),
            "one_line_idea": "Selective long-term memory retrieval for evidence-grounded counseling documentation.",
            "contribution_candidates": [
                "A longitudinal counseling-memory retrieval formulation.",
                "An evidence-linked documentation generation pipeline.",
                "A counselor-in-the-loop verification workflow.",
                "Evaluation metrics for evidence coverage, faithfulness, and review burden.",
            ],
            "reviewer_risks": [
                "Novelty may look incremental if framed as generic RAG.",
                "Dataset access and privacy constraints can weaken the empirical story.",
                "Counseling safety boundaries must be explicit: the system assists documentation, not diagnosis.",
            ],
        }
    if task_type == "remind_mvp":
        return {
            "problem": (
                "Counselors spend substantial time converting messy session notes, transcripts, and prior summaries "
                "into structured documentation that still requires careful review."
            ),
            "gap": (
                "Many note-generation tools optimize draft fluency but provide weak source verification and weak "
                "support for prior-session continuity."
            ),
            "core_research_question": (
                "How can a counselor-facing documentation assistant reduce review burden while preserving source "
                "traceability and counselor control?"
            ),
            "one_line_idea": "Evidence-linked Re:mind documentation drafts with a counselor review workflow.",
            "contribution_candidates": [
                "A source-verification interface for generated counseling notes.",
                "A structured note schema that separates observed facts from counselor-review fields.",
                "A lightweight user test protocol for measuring review burden.",
            ],
            "reviewer_risks": [
                "Product value may be hard to separate from generic summarization.",
                "Counselor trust depends on visible evidence, not only polished text.",
            ],
        }
    if task_type == "professor_outreach":
        return {
            "problem": (
                "The student's research interests span LLMs, RAG, mental-health QA, safety-aware refinement, and "
                "Re:mind, but outreach needs a coherent fit narrative."
            ),
            "gap": "A broad AI profile can look unfocused unless tied to specific professor themes and concrete artifacts.",
            "core_research_question": (
                "How can the student's research narrative be positioned around evidence-grounded, safety-aware LLM "
                "systems for high-stakes support tasks?"
            ),
            "one_line_idea": "A focused outreach story around evidence-grounded LLM systems for counseling documentation.",
            "contribution_candidates": [
                "A professor-specific fit matrix.",
                "A concise email angle supported by one project artifact.",
                "A meeting prep checklist with technical and research questions.",
            ],
            "reviewer_risks": [
                "Emails may sound generic without naming the professor's concrete work.",
                "The project may seem product-heavy unless the research question is foregrounded.",
            ],
        }
    return {
        "problem": "The current idea combines research, product, and execution needs without a clear first decision.",
        "gap": "The plan lacks a narrow hypothesis, evaluation route, and two-day execution boundary.",
        "core_research_question": "What is the smallest research or product hypothesis that can be tested this week?",
        "one_line_idea": "Convert broad ideas into a narrow testable plan with explicit evidence and priorities.",
        "contribution_candidates": [
            "A clarified hypothesis.",
            "A minimal validation artifact.",
            "A measurable 48-hour execution plan.",
        ],
        "reviewer_risks": [
            "The idea can remain too vague without a target user or target venue.",
            "Execution can drift into tooling instead of learning.",
        ],
    }


def literature_scout(user_input: str, triage: dict[str, Any], research: dict[str, Any]) -> dict[str, Any]:
    task_type = triage["task_type"]
    if task_type == "wsdm_paper":
        areas = [
            "Retrieval-augmented generation for evidence-grounded generation.",
            "Long-context and long-term memory for LLM conversations.",
            "Conversational memory retrieval and temporal relevance.",
            "Clinical or counseling documentation summarization.",
            "Human-AI verification interfaces and source attribution.",
        ]
        queries = [
            "selective memory retrieval counseling documentation RAG",
            "evidence grounded generation source attribution LLM",
            "long-term conversational memory retrieval evaluation",
            "clinical documentation summarization human verification",
        ]
    elif task_type == "remind_mvp":
        areas = [
            "Clinical documentation summarization and note drafting.",
            "Human-AI verification workflows.",
            "Source attribution interfaces for high-stakes LLM output.",
            "Counselor workflow and documentation burden.",
        ]
        queries = [
            "counseling documentation AI source verification",
            "clinical note summarization review burden LLM",
            "human AI verification source attribution interface",
        ]
    elif task_type == "professor_outreach":
        areas = [
            "RAG and evidence-grounded generation.",
            "Mental-health LLM evaluation.",
            "Safety-aware response refinement.",
            "Human-centered AI systems for high-stakes domains.",
        ]
        queries = [
            "mental health LLM evaluation RAG safety",
            "evidence grounded generation high stakes LLM",
            "safety aware response refinement LLM",
        ]
    else:
        areas = [
            "Research question formulation.",
            "Evidence-grounded LLM systems.",
            "Human-in-the-loop evaluation.",
        ]
        queries = [research["one_line_idea"], research["core_research_question"]]

    seed_papers: list[dict[str, Any]] = []
    for query in queries:
        for paper in search_local_papers(query, top_k=3):
            if paper.get("title") not in {item.get("title") for item in seed_papers}:
                seed_papers.append(paper)
            if len(seed_papers) >= 5:
                break
        if len(seed_papers) >= 5:
            break

    if not seed_papers:
        seed_papers = [
            {
                "title": "Sample local paper card: Evidence-grounded LLM Systems",
                "year": 2024,
                "venue": "Local demo database",
                "tags": ["RAG", "evidence-grounding", "verification"],
                "abstract": "A placeholder card for evidence-linked generation and verification workflows.",
                "why_relevant": "Fallback card when keyword search finds no direct match.",
            }
        ]

    return {
        "related_work_areas": areas,
        "search_queries": queries,
        "seed_papers": seed_papers[:5],
        "reading_priority": [
            "Read one survey or overview for terminology alignment.",
            "Read two papers on evidence/source attribution interfaces.",
            "Read two papers closest to the task domain before expanding the search.",
        ],
    }


def experiment_designer(user_input: str, triage: dict[str, Any], research: dict[str, Any]) -> dict[str, Any]:
    task_type = triage["task_type"]
    if task_type == "wsdm_paper":
        return {
            "datasets": [
                "real counselor records if available",
                "PsychEval",
                "ESConv",
                "synthetic multi-session counseling data",
            ],
            "baselines": [
                "no memory",
                "full history",
                "BM25 retrieval",
                "vector retrieval",
                "selective memory retrieval",
            ],
            "metrics": [
                "evidence precision",
                "summary faithfulness",
                "documentation completeness",
                "review burden proxy",
                "safety boundary violation",
            ],
            "ablations": [
                "remove temporal recency features",
                "remove evidence-link requirement",
                "compare prior-session only vs full longitudinal memory",
                "vary top-k retrieved memories",
            ],
            "minimum_viable_experiment": (
                "Create 20 to 50 synthetic multi-session counseling cases, implement no-memory, full-history, "
                "BM25, and selective retrieval baselines, then score evidence coverage and faithfulness on a fixed note schema."
            ),
            "feasibility_notes": [
                "Use synthetic cases first if real records are blocked by privacy review.",
                "Keep the first experiment offline and file-based.",
                "Manually inspect 5 examples before scaling metrics.",
            ],
        }
    if task_type == "remind_mvp":
        return {
            "datasets": [
                "synthetic counseling session memos",
                "sample transcripts with previous-session summaries",
                "counselor feedback notes from lightweight interviews",
            ],
            "baselines": ["manual note drafting", "plain LLM summary", "structured LLM summary without evidence links"],
            "metrics": [
                "time to review",
                "number of unsupported claims found",
                "counselor trust rating",
                "edit distance from accepted note",
            ],
            "ablations": [
                "with vs without evidence mapping",
                "with vs without previous-session summary",
                "structured fields vs free-form draft",
            ],
            "minimum_viable_experiment": (
                "Run 3 to 5 counselor-style walkthroughs using synthetic notes and compare plain summary drafts "
                "against evidence-linked structured drafts."
            ),
            "feasibility_notes": [
                "Do not add authentication or persistence before validating review value.",
                "Use local JSON examples to avoid handling real counseling data.",
            ],
        }
    if task_type == "professor_outreach":
        return {
            "datasets": ["target professor paper list", "student project summaries", "one-page Re:mind artifact"],
            "baselines": ["generic email", "topic-only email", "professor-specific fit email"],
            "metrics": ["specificity of fit", "clarity of ask", "artifact readiness", "response likelihood proxy"],
            "ablations": ["with vs without concrete project artifact", "broad AI pitch vs narrow evidence-grounding pitch"],
            "minimum_viable_experiment": "Draft 3 professor-specific emails and score each against a fit rubric before sending.",
            "feasibility_notes": [
                "Do not send mass emails.",
                "Prepare one concrete technical artifact link or PDF before outreach.",
            ],
        }
    return {
        "datasets": ["user idea dump", "small sample examples", "manual evaluation notes"],
        "baselines": ["do nothing", "manual planning", "single-agent summary"],
        "metrics": ["clarity", "feasibility", "time to first artifact", "decision confidence"],
        "ablations": ["remove reviewer step", "remove priority scoring"],
        "minimum_viable_experiment": "Produce one artifact in 48 hours and evaluate whether it answers the core question.",
        "feasibility_notes": ["Start with local files and deterministic outputs.", "Avoid new infrastructure this week."],
    }


def startup_validator(user_input: str, triage: dict[str, Any], research: dict[str, Any]) -> dict[str, Any]:
    task_type = triage["task_type"]
    if task_type in {"wsdm_paper", "remind_mvp"}:
        return {
            "target_users": [
                "school counselors",
                "private-practice counselors",
                "counseling interns who need supervision-ready drafts",
            ],
            "pain_points": [
                "Session notes are messy and time-consuming to turn into structured records.",
                "Prior-session context is hard to retrieve at the right level of detail.",
                "Generated drafts are hard to trust without source evidence.",
            ],
            "mvp_feature": "Evidence-linked note draft preview that maps each generated claim to the session memo, transcript, or prior summary.",
            "validation_questions": [
                "Does evidence mapping reduce counselor review time?",
                "Which fields require explicit counselor review before export?",
                "Do counselors prefer prior-session summaries, retrieved snippets, or both?",
            ],
            "business_value": (
                "Re:mind can differentiate on trust and review workflow rather than only generating fluent notes."
            ),
            "startup_risks": [
                "Counseling data privacy and consent constraints.",
                "Overclaiming clinical decision support instead of documentation assistance.",
                "Workflow friction if evidence links are too noisy.",
            ],
        }
    if task_type == "professor_outreach":
        return {
            "target_users": ["prospective advisors", "graduate admissions readers", "research lab members"],
            "pain_points": [
                "They receive generic outreach messages.",
                "They need quick evidence that the student understands the lab's work.",
            ],
            "mvp_feature": "Professor-specific fit packet: 3-sentence email angle, project artifact, and meeting questions.",
            "validation_questions": [
                "Does the email name a concrete research fit?",
                "Does the artifact show implementation ability?",
                "Is the ask small and easy to answer?",
            ],
            "business_value": "Better outreach can convert existing projects into credible research conversations.",
            "startup_risks": ["Generic messaging", "Weak link between project and professor agenda"],
        }
    return {
        "target_users": ["student researcher", "early-stage founder"],
        "pain_points": [
            "Too many possible directions.",
            "Unclear next action.",
            "Hard to balance research novelty with product value.",
        ],
        "mvp_feature": "A file-based research-to-action brief generator.",
        "validation_questions": [
            "Does the plan produce a useful artifact in two days?",
            "Does the reviewer critique change the next action?",
        ],
        "business_value": "The assistant helps convert ambiguity into progress without extra infrastructure.",
        "startup_risks": ["May remain a planning tool unless connected to measurable outcomes."],
    }


def execution_planner(
    user_input: str,
    triage: dict[str, Any],
    research: dict[str, Any],
    experiment: dict[str, Any],
    startup: dict[str, Any],
) -> dict[str, Any]:
    task_type = triage["task_type"]
    if task_type == "wsdm_paper":
        today = [
            "Decide dataset route: real counselor records, PsychEval, ESConv, or synthetic multi-session cases.",
            "Create the output document schema with evidence-link fields.",
            "Collect 5 seed papers for RAG, long-term memory, clinical documentation, and source attribution.",
        ]
        tomorrow = [
            "Build a tiny retrieval baseline table: no memory, full history, BM25, vector retrieval, selective retrieval.",
            "Write 10 synthetic multi-session examples and label relevant prior-session evidence.",
            "Draft the WSDM problem/gap paragraph and one figure sketch.",
        ]
        this_week = [
            "Run the first offline pilot on 20 to 50 examples.",
            "Create an error taxonomy for unsupported evidence, missing continuity, and safety-boundary issues.",
            "Prepare a one-page advisor update with pilot results and dataset decision.",
        ]
        do_not = [
            "frontend redesign",
            "full backend implementation",
            "reading 30 papers randomly",
            "marketing content generation",
        ]
    elif task_type == "remind_mvp":
        today = [
            "Pick one MVP feature: evidence-linked note draft preview.",
            "Write 3 synthetic counselor workflow scenarios.",
            "Define success metrics for review burden and unsupported-claim detection.",
        ]
        tomorrow = [
            "Create a clickable or Streamlit-level demo using local JSON examples.",
            "Run a self-review against the verification report fields.",
            "Draft 5 counselor interview questions.",
        ]
        this_week = [
            "Conduct 3 lightweight walkthroughs with synthetic data.",
            "Compare plain summary vs evidence-linked structured draft.",
            "Decide whether previous-session retrieval is the next build target.",
        ]
        do_not = ["authentication", "database design", "audio upload", "payment", "production deployment"]
    elif task_type == "professor_outreach":
        today = [
            "Create a 5-column professor fit matrix.",
            "Write one narrow research narrative around evidence-grounded LLM systems.",
            "Prepare a one-page Re:mind technical artifact summary.",
        ]
        tomorrow = [
            "Draft 3 professor-specific emails.",
            "Add two concrete paper references per professor.",
            "Prepare 5 meeting questions that connect to each lab's agenda.",
        ]
        this_week = [
            "Send the first 2 carefully customized emails.",
            "Track replies and update the fit matrix.",
            "Refine the project artifact based on the strongest lab fit.",
        ]
        do_not = ["mass-email professors", "send generic AI interest emails", "overclaim unpublished results"]
    else:
        today = [
            "Write the one-sentence hypothesis.",
            "Choose one evaluation signal.",
            "Create one small artifact that can be inspected tomorrow.",
        ]
        tomorrow = [
            "Run the smallest possible test.",
            "Capture failure cases.",
            "Revise the plan based on evidence.",
        ]
        this_week = [
            "Decide whether to continue, pivot, or stop.",
            "Prepare a short update message.",
        ]
        do_not = ["add infrastructure", "expand to three ideas", "polish before testing"]

    priority_ranking = []
    all_items = today + tomorrow + this_week
    for index, item in enumerate(all_items, start=1):
        impact = 5 if index <= 3 else 4
        urgency = 5 if item in today else 3
        feasibility = 4 if len(item) < 120 else 3
        priority_ranking.append(
            {
                "item": item,
                "impact": impact,
                "urgency": urgency,
                "feasibility": feasibility,
                "score": score_priority(impact, urgency, feasibility),
            }
        )
    priority_ranking.sort(key=lambda row: row["score"], reverse=True)

    return {
        "today": today,
        "tomorrow": tomorrow,
        "this_week": this_week,
        "priority_ranking": priority_ranking,
        "do_not_do_today": do_not,
    }


def harsh_reviewer(
    user_input: str,
    triage: dict[str, Any],
    research: dict[str, Any],
    experiment: dict[str, Any],
    startup: dict[str, Any],
    action_plan: dict[str, Any],
) -> dict[str, Any]:
    task_type = triage["task_type"]
    dataset_missing = task_type == "wsdm_paper" and not any(
        word in user_input.lower() for word in ["dataset", "data", "psycheval", "esconv", "records"]
    )
    if task_type == "wsdm_paper":
        return {
            "novelty_score": 4,
            "feasibility_score": 3 if dataset_missing else 4,
            "clarity_score": 4,
            "main_weakness": (
                "The idea becomes publishable only if selective longitudinal retrieval is evaluated as a distinct "
                "problem rather than described as a generic RAG pipeline."
            ),
            "required_revision": (
                "Lock the dataset route and define evidence-level labels before expanding the system implementation."
            ),
            "acceptance_potential": "medium-high",
        }
    if task_type == "remind_mvp":
        return {
            "novelty_score": 3,
            "feasibility_score": 5,
            "clarity_score": 4,
            "main_weakness": "The MVP must prove trust and review-burden value, not just produce nicer summaries.",
            "required_revision": "Make evidence mapping the primary demo and measure counselor review actions.",
            "acceptance_potential": "medium",
        }
    if task_type == "professor_outreach":
        return {
            "novelty_score": 3,
            "feasibility_score": 5,
            "clarity_score": 4,
            "main_weakness": "The outreach story can sound broad unless every message names a specific lab fit.",
            "required_revision": "Attach one concrete artifact and two professor-specific paper hooks to each email.",
            "acceptance_potential": "medium-high",
        }
    return {
        "novelty_score": 3,
        "feasibility_score": 4,
        "clarity_score": 3,
        "main_weakness": "The plan needs a sharper hypothesis and evaluation signal.",
        "required_revision": "Choose one output artifact and one success metric for the next 48 hours.",
        "acceptance_potential": "medium",
    }


def report_writer(user_input: str, agent_outputs: dict[str, Any], warnings: list[str]) -> dict[str, str]:
    triage = agent_outputs["Intake & Triage Agent"]
    research = agent_outputs["Research Question Architect"]
    literature = agent_outputs["Literature Scout"]
    experiment = agent_outputs["Experiment Designer"]
    startup = agent_outputs["Startup Validator"]
    action = agent_outputs["Execution Planner"]
    review = agent_outputs["Harsh Reviewer"]

    advisor_message = _advisor_message(triage, research, experiment)
    brief = "\n".join(
        [
            "# ResearchPilot Brief",
            "",
            "## 1. Input Summary",
            shorten(user_input.replace("\n", " "), width=700, placeholder="..."),
            "",
            "## 2. Task Type and Route",
            f"- Task type: {triage['task_type']}",
            f"- Urgency: {triage['urgency']}",
            f"- Main goal: {triage['main_goal']}",
            f"- Recommended route: {triage['recommended_route']}",
            _warnings_block(warnings),
            "",
            "## 3. Core Research Question",
            research["core_research_question"],
            "",
            "## 4. Problem and Gap",
            f"Problem: {research['problem']}",
            "",
            f"Gap: {research['gap']}",
            "",
            "## 5. One-Line Idea",
            research["one_line_idea"],
            "",
            "## 6. Contribution Candidates",
            _numbered(research["contribution_candidates"]),
            "",
            "## 7. Related Work Directions",
            _bullets(literature["related_work_areas"]),
            "",
            "Search queries:",
            _bullets(literature["search_queries"]),
            "",
            "Seed papers from local demo database:",
            _paper_bullets(literature["seed_papers"]),
            "",
            "## 8. Experiment Plan",
            "Datasets:",
            _bullets(experiment["datasets"]),
            "",
            "Baselines:",
            _bullets(experiment["baselines"]),
            "",
            "Metrics:",
            _bullets(experiment["metrics"]),
            "",
            "Ablations:",
            _bullets(experiment["ablations"]),
            "",
            f"Minimum viable experiment: {experiment['minimum_viable_experiment']}",
            "",
            "## 9. Startup/MVP Connection",
            f"MVP feature: {startup['mvp_feature']}",
            "",
            "Target users:",
            _bullets(startup["target_users"]),
            "",
            "Pain points:",
            _bullets(startup["pain_points"]),
            "",
            f"Business value: {startup['business_value']}",
            "",
            "Validation questions:",
            _bullets(startup["validation_questions"]),
            "",
            "## 10. Reviewer Risks",
            _bullets(research["reviewer_risks"] + startup["startup_risks"]),
            "",
            "## 11. Harsh Reviewer Feedback",
            f"- Novelty score: {review['novelty_score']}/5",
            f"- Feasibility score: {review['feasibility_score']}/5",
            f"- Clarity score: {review['clarity_score']}/5",
            f"- Main weakness: {review['main_weakness']}",
            f"- Required revision: {review['required_revision']}",
            f"- Acceptance potential: {review['acceptance_potential']}",
            "",
            "## 12. 48-Hour Execution Plan",
            "Today:",
            _numbered(action["today"]),
            "",
            "Tomorrow:",
            _numbered(action["tomorrow"]),
            "",
            "This week:",
            _numbered(action["this_week"]),
            "",
            "Priority ranking:",
            _priority_lines(action["priority_ranking"][:8]),
            "",
            "## 13. Do Not Do Today",
            _bullets(action["do_not_do_today"]),
            "",
            "## 14. Advisor Update Message",
            advisor_message,
            "",
        ]
    )
    return {
        "research_brief": brief,
        "advisor_message": advisor_message,
        "action_plan_markdown": _action_plan_markdown(action),
        "run_summary": (
            f"Ran route {triage['task_type']} with 8 mock agents. "
            f"Warnings: {len(warnings)}. Reviewer potential: {review['acceptance_potential']}."
        ),
    }


def _advisor_message(triage: dict[str, Any], research: dict[str, Any], experiment: dict[str, Any]) -> str:
    if triage["task_type"] == "wsdm_paper":
        return (
            "Professor, I organized the WSDM follow-up direction around selective long-term memory retrieval and "
            "evidence-grounded counseling documentation. The core question is which prior-session information should "
            "be retrieved for the current counseling record and how each generated sentence can be linked back to "
            "source evidence. This week I plan to finalize the dataset route, define the document schema, and build "
            "a small pilot with baseline retrieval settings."
        )
    if triage["task_type"] == "remind_mvp":
        return (
            "Professor, I narrowed the Re:mind MVP direction to evidence-linked note draft preview. The goal is to "
            "test whether source mapping reduces counselor review burden compared with plain note generation. This "
            "week I will prepare synthetic walkthrough cases, define review metrics, and run a small validation pass."
        )
    if triage["task_type"] == "professor_outreach":
        return (
            "Professor, I am preparing outreach around evidence-grounded and safety-aware LLM systems for high-stakes "
            "support tasks. I will build a professor fit matrix, attach a concise Re:mind artifact, and draft targeted "
            "emails that connect my implementation experience to each lab's current research."
        )
    return (
        "Professor, I converted the broad idea into a narrow testable plan. The immediate goal is to produce one "
        "inspectable artifact, evaluate it with a simple success signal, and use the result to decide the next direction."
    )


def _bullets(items: list[Any]) -> str:
    if not items:
        return "- None specified."
    return "\n".join(f"- {item}" for item in items)


def _numbered(items: list[Any]) -> str:
    if not items:
        return "1. None specified."
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1))


def _paper_bullets(papers: list[dict[str, Any]]) -> str:
    lines = []
    for paper in papers:
        tags = ", ".join(paper.get("tags", []))
        lines.append(
            f"- {paper.get('title', 'Untitled')} ({paper.get('year', 'n.d.')}, "
            f"{paper.get('venue', 'local')}) - {paper.get('why_relevant', '')} Tags: {tags}."
        )
    return "\n".join(lines) if lines else "- No local paper cards found."


def _priority_lines(priority_ranking: list[dict[str, Any]]) -> str:
    if not priority_ranking:
        return "- No priorities generated."
    return "\n".join(f"- {row['score']}: {row['item']}" for row in priority_ranking)


def _warnings_block(warnings: list[str]) -> str:
    if not warnings:
        return "- Warnings: none"
    return "- Warnings:\n" + "\n".join(f"  - {warning}" for warning in warnings)


def _action_plan_markdown(action: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# ResearchPilot Action Plan",
            "",
            "## Today",
            _numbered(action["today"]),
            "",
            "## Tomorrow",
            _numbered(action["tomorrow"]),
            "",
            "## This Week",
            _numbered(action["this_week"]),
            "",
            "## Do Not Do Today",
            _bullets(action["do_not_do_today"]),
            "",
        ]
    )
