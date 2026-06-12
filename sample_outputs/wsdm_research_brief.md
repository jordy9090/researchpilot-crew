# ResearchPilot Brief

## 1. Input Summary
I want to develop a WSDM full paper from Re:mind. The topic is long-term memory retrieval and evidence-grounded counseling documentation. I need a research question, related work direction, experiment plan, MVP connection, and this week's TODO. Data may come from real counselor records, PsychEval, ESConv, or synthetic multi-session counseling data.

## 2. Task Type and Route
- Task type: wsdm_paper
- Urgency: high
- Main goal: Shape a WSDM-style research direction from Re:mind into an experiment-ready paper plan.
- Recommended route: wsdm_paper -> research question -> literature -> experiment -> MVP link -> 48-hour plan
- Warnings: none

## 3. Core Research Question
How can an LLM-based counseling documentation system selectively retrieve prior-session information that is relevant, temporally valid, and evidence-grounded for the current counseling record?

## 4. Problem and Gap
Problem: Counseling documentation often requires connecting the current session to prior goals, symptoms, interventions, homework, and risk signals. Full-history prompting is costly and noisy, while no-memory generation misses longitudinal context.

Gap: Existing single-turn mental-health QA and generic RAG systems do not directly address longitudinal evidence selection for counseling documentation.

## 5. One-Line Idea
Selective long-term memory retrieval for evidence-grounded counseling documentation.

## 6. Contribution Candidates
1. A longitudinal counseling-memory retrieval formulation.
2. An evidence-linked documentation generation pipeline.
3. A counselor-in-the-loop verification workflow.
4. Evaluation metrics for evidence coverage, faithfulness, and review burden.

## 7. Related Work Directions
- Retrieval-augmented generation for evidence-grounded generation.
- Long-context and long-term memory for LLM conversations.
- Conversational memory retrieval and temporal relevance.
- Clinical or counseling documentation summarization.
- Human-AI verification interfaces and source attribution.

Search queries:
- selective memory retrieval counseling documentation RAG
- evidence grounded generation source attribution LLM
- long-term conversational memory retrieval evaluation
- clinical documentation summarization human verification

Seed papers from local demo database:
- Sample local paper card: Counseling Documentation Workflow (2025, Local demo database) - Connects the research plan to Re:mind's target user workflow. Tags: counseling, documentation, workflow, MVP.
- Sample local paper card: Conversational Memory Retrieval (2023, Local demo database) - Directly informs prior-session memory selection and temporal validity. Tags: conversation, memory, retrieval, temporal-relevance.
- Sample local paper card: Retrieval-Augmented Generation Foundations (2024, Local demo database) - Frames the baseline comparison between no memory, retrieved context, and evidence-grounded generation. Tags: RAG, retrieval, LLM, evidence-grounding.
- Sample local paper card: Evidence-Grounded Generation with Source Links (2024, Local demo database) - Matches the evidence mapping requirement for Re:mind notes. Tags: evidence-grounding, source-attribution, faithfulness, LLM.
- Sample local paper card: Source Attribution Interfaces (2023, Local demo database) - Helps design the document transform preview and evidence-linked draft. Tags: source-attribution, interface, explainability, HCI.

## 8. Experiment Plan
Datasets:
- real counselor records if available
- PsychEval
- ESConv
- synthetic multi-session counseling data

Baselines:
- no memory
- full history
- BM25 retrieval
- vector retrieval
- selective memory retrieval

Metrics:
- evidence precision
- summary faithfulness
- documentation completeness
- review burden proxy
- safety boundary violation

Ablations:
- remove temporal recency features
- remove evidence-link requirement
- compare prior-session only vs full longitudinal memory
- vary top-k retrieved memories

Minimum viable experiment: Create 20 to 50 synthetic multi-session counseling cases, implement no-memory, full-history, BM25, and selective retrieval baselines, then score evidence coverage and faithfulness on a fixed note schema.

## 9. Startup/MVP Connection
MVP feature: Evidence-linked note draft preview that maps each generated claim to the session memo, transcript, or prior summary.

Target users:
- school counselors
- private-practice counselors
- counseling interns who need supervision-ready drafts

Pain points:
- Session notes are messy and time-consuming to turn into structured records.
- Prior-session context is hard to retrieve at the right level of detail.
- Generated drafts are hard to trust without source evidence.

Business value: Re:mind can differentiate on trust and review workflow rather than only generating fluent notes.

Validation questions:
- Does evidence mapping reduce counselor review time?
- Which fields require explicit counselor review before export?
- Do counselors prefer prior-session summaries, retrieved snippets, or both?

## 10. Reviewer Risks
- Novelty may look incremental if framed as generic RAG.
- Dataset access and privacy constraints can weaken the empirical story.
- Counseling safety boundaries must be explicit: the system assists documentation, not diagnosis.
- Counseling data privacy and consent constraints.
- Overclaiming clinical decision support instead of documentation assistance.
- Workflow friction if evidence links are too noisy.

## 11. Harsh Reviewer Feedback
- Novelty score: 4/5
- Feasibility score: 4/5
- Clarity score: 4/5
- Main weakness: The idea becomes publishable only if selective longitudinal retrieval is evaluated as a distinct problem rather than described as a generic RAG pipeline.
- Required revision: Lock the dataset route and define evidence-level labels before expanding the system implementation.
- Acceptance potential: medium-high

## 12. 48-Hour Execution Plan
Today:
1. Decide dataset route: real counselor records, PsychEval, ESConv, or synthetic multi-session cases.
2. Create the output document schema with evidence-link fields.
3. Collect 5 seed papers for RAG, long-term memory, clinical documentation, and source attribution.

Tomorrow:
1. Build a tiny retrieval baseline table: no memory, full history, BM25, vector retrieval, selective retrieval.
2. Write 10 synthetic multi-session examples and label relevant prior-session evidence.
3. Draft the WSDM problem/gap paragraph and one figure sketch.

This week:
1. Run the first offline pilot on 20 to 50 examples.
2. Create an error taxonomy for unsupported evidence, missing continuity, and safety-boundary issues.
3. Prepare a one-page advisor update with pilot results and dataset decision.

Priority ranking:
- 4.8: Decide dataset route: real counselor records, PsychEval, ESConv, or synthetic multi-session cases.
- 4.8: Create the output document schema with evidence-link fields.
- 4.8: Collect 5 seed papers for RAG, long-term memory, clinical documentation, and source attribution.
- 3.65: Build a tiny retrieval baseline table: no memory, full history, BM25, vector retrieval, selective retrieval.
- 3.65: Write 10 synthetic multi-session examples and label relevant prior-session evidence.
- 3.65: Draft the WSDM problem/gap paragraph and one figure sketch.
- 3.65: Run the first offline pilot on 20 to 50 examples.
- 3.65: Create an error taxonomy for unsupported evidence, missing continuity, and safety-boundary issues.

## 13. Do Not Do Today
- frontend redesign
- full backend implementation
- reading 30 papers randomly
- marketing content generation

## 14. Advisor Update Message
Professor, I organized the WSDM follow-up direction around selective long-term memory retrieval and evidence-grounded counseling documentation. The core question is which prior-session information should be retrieved for the current counseling record and how each generated sentence can be linked back to source evidence. This week I plan to finalize the dataset route, define the document schema, and build a small pilot with baseline retrieval settings.
