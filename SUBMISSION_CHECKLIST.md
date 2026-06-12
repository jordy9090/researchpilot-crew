# Submission Checklist

## Homework #2: ResearchPilot Crew

Framework: CrewAI

Recommended run command:

```bash
pip install -r requirements.txt
python main.py --mode mock --input data/sample_inputs/wsdm_idea.txt
```

Optional smoke test:

```bash
python smoke_test.py
```

Streamlit demo:

```bash
streamlit run app.py
```

Submitted files:

- source code
- `README.md`
- `REPORT.md`
- sample input files
- sample outputs
- `smoke_test.py`

API keys:

- No API keys are included.
- `.env` is ignored by git.
- `.env.example` contains empty placeholders only.

Expected outputs:

- `outputs/research_brief.md`
- `outputs/advisor_message.md`
- `outputs/action_plan.json`
- `outputs/agent_outputs.json`
- `outputs/run_log.json`
