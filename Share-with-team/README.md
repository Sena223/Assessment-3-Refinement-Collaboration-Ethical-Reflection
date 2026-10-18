# A3 Resume Pre-Screening Agent: how to import and run

An n8n agentic workflow that pre-screens one job application at a time for an Australian employer. It checks the job ad for discriminatory criteria, scores the resume against the lawful criteria with quoted evidence, grounds policy and legal judgements in a knowledge base (hybrid RAG), has a second model review the scoring, and routes every case to **SHORTLIST**, **HUMAN_CONFIRM_REJECTION** or **HUMAN_REVIEW**. It is decision support: it never rejects a candidate on its own.

Tested with **n8n 2.35.7** (self-hosted, macOS), RMIT Val as the model provider, and Google Gemini embeddings.

---

## 1. What is in this package

```
workflows/
  A3_Resume_PreScreening_Agent.json   main workflow (import this)
  A3_Tool_keyword_search.json         BM25 keyword-search tool called by the agent (import and PUBLISH)
  A3_Tool_retrieval_check.json        optional: measures retrieval quality on test questions
data/                                 copy this whole folder to ~/.n8n-files/a3/ (see step 2)
  config/run-config.json              which job ad and resume to screen, and the test switches
  config/retrieval-tests.json         test questions for the retrieval check
  kb/*.md                             knowledge base (chunked, with metadata headers)
  jobs/*.md                           job ads (criteria lines start E1:, D1: ...)
  resumes/*.md                        fictional resumes
  prompts/screening_agent.md          system prompt for the screening agent
  prompts/reviewer.md                 system prompt for the reviewer
  logs/                               one JSON run log per execution is written here
scripts/
  run_batch.py                        optional: runs a CSV of test cases through n8n and summarises them
  batches/*.csv                       batch definitions and their results
```

Prompts and knowledge-base files are plain text. You can edit them without touching n8n. Notes inside `<!-- ... -->` are annotations and are **not** sent to the models.

---

## 2. Setup (about 10 minutes)

**Step 1: Credentials.** In n8n go to *Overview → Credentials → Create credential* and create two. **The names must match exactly**, because the workflows look them up by name:

| Credential name | Type | Settings |
|---|---|---|
| `VAL` | OpenAI | API key: your RMIT Val key · Base URL: `https://val.rmit.edu.au/api` |
| `Gemini` | Google Gemini(PaLM) Api | API key from aistudio.google.com/apikey (the free tier is enough); keep the default host |

Without RMIT Val, any OpenAI-compatible endpoint works: put its base URL in `VAL` and change the model IDs in the three chat-model nodes (`VAL GPT-4.1 (screener)`, `VAL GPT-4.1 (screener, no KB)`, `VAL Claude Haiku 4.5 (reviewer)`).

**Step 2: Data folder.** n8n 2.x only lets workflows read files under `~/.n8n-files/` by default. Copy the `data` folder so the files sit at:
- macOS/Linux: `/Users/<you>/.n8n-files/a3/` (or `/home/<you>/.n8n-files/a3/`)
- Windows: `C:\Users\<you>\.n8n-files\a3\`

If your path is not `/Users/sean/.n8n-files/a3`, open the **Settings** node in *each* of the three workflows and change `data_dir` to your path.

Note: If you edit a job advertisement, resume or prompt in the GitHub project folder, copy the updated file into ~/.n8n-files/a3/ before running the workflow. n8n reads from this local directory, not directly from the GitHub repository.

**Step 3: Import.** *Workflows → Import from file* for each JSON in `workflows/`. Or use the command line:
```
n8n import:workflow --input=workflows/A3_Tool_keyword_search.json
n8n import:workflow --input=workflows/A3_Resume_PreScreening_Agent.json
n8n import:workflow --input=workflows/A3_Tool_retrieval_check.json
```
If a credential shows a warning after importing, open the node and re-select `VAL` or `Gemini`.

**Step 4: Publish the tool workflow (required).** Open **A3 Tool - keyword_search (BM25)** and click **Publish**, or run `n8n publish:workflow --id=A3KeywordSearch1`. n8n 2.x refuses to run an unpublished sub-workflow as an agent tool ("Workflow is not active and cannot be executed").

---

## 3. Run one screening

1. Edit `data/config/run-config.json` in your `~/.n8n-files/a3/` copy:

| Field | Meaning |
|---|---|
| `job_file`, `resume_file` | paths relative to the data folder, e.g. `jobs/J01_….md` |
| `retrieval_mode` | `hybrid` = knowledge base on (keyword + semantic search); `none` = no knowledge base (used for the with/without-RAG comparison) |
| `redact_identifiers` | `true` hides the name, contact details and age clues before any model sees the resume; `false` sends the resume as written (used in bias tests) |
| `max_attempts` | total screening attempts allowed, including reviewer-requested redos (default 3) |
| `top_k` | chunks returned per keyword search (default 4) |
| `run_label`, `case_id`, `variant`, `repeat` | labels copied into the run log |

2. Open **A3 Resume Pre-Screening Agent** and click **Execute workflow**. One run takes about 10–40 seconds.
3. The route appears on one of the three end nodes: `Shortlist (auto)`, `Recruiter: confirm rejection` or `Recruiter: review`. The **Gate** node shows the reasons.
4. A full run log is written to `logs/`. It records the platform, models, timestamp, n8n execution ID and context, the job-ad check, the redaction, every attempt (searches, retrieved chunk IDs, automated-check results, reviewer verdict), the final scores and the route with reasons.

## 4. Run a batch (optional)

```
python3 scripts/run_batch.py scripts/batches/example_batch.csv
```
Each CSV row is a case; `repeats` runs it several times (bias tests use 5). The script needs the `n8n` command on your PATH (or `N8N_BIN=/path/to/n8n/bin`), and writes `results_<batch>.csv` next to the batch file, with one line per run.

## 5. Check retrieval quality (optional)

Put test questions and their expected chunk IDs in `data/config/retrieval-tests.json`, then execute **A3 Tool - retrieval check**. The report written to `logs/retrieval-check__exec<ID>.json` gives hit rate, recall, precision and MRR at top-4 for keyword, semantic and hybrid retrieval.

---

## 6. How the workflow is put together

| Stage | Nodes | What happens |
|---|---|---|
| Load | Settings → Read case files → Assemble case | Reads the config, job ad, resume and prompts; parses the E/D criteria |
| Stage 0 | Job-ad criteria check | Coded or discriminatory criteria (age, sex, race/national origin, disability, family status, religion) are **excluded** from scoring; criteria needing confirmation (physical, citizenship, long experience) are flagged |
| Privacy | Privacy redaction | Optional redaction of identifiers and age clues; detects policy-sensitive content and possible prompt injection |
| Knowledge base | Read KB files → Chunk KB → Index KB (vector store) | Parses `## CHUNK:` blocks with metadata; embeds title + keywords + text with Gemini into n8n's in-memory vector store |
| Agent | Prepare attempt → Screening agent | GPT-4.1 agent with two tools: `keyword_search` (BM25 sub-workflow) and `semantic_search` (vector store). It decides what and when to search |
| Verify | Verify output | Code checks: every criterion scored, quotes verbatim from the resume, cited chunks actually retrieved in this run, search done where policy-sensitive content exists, protected-attribute mentions |
| Review | Reviewer (Claude) → Decide | Claude Haiku 4.5 reviews the scoring with the retrieved chunk text; failed checks or a REDO verdict send the agent back with its previous answer and the feedback (up to `max_attempts`) |
| Gate | Gate → Route | Code decides: SHORTLIST only if every essential criterion ≥ 2 and nothing is flagged; every rejection goes to a recruiter to confirm; everything else goes to human review |
| Log | Build run log → Write run log | JSON record of the whole run |

## 7. Troubleshooting

| Message | Fix |
|---|---|
| `Node "…" uses invalid credential` | A credential named exactly `VAL` or `Gemini` is missing. n8n checks every enabled node before running |
| `Workflow is not active and cannot be executed` | Publish **A3 Tool - keyword_search (BM25)** (step 4) |
| `Access to the file is not allowed` | The data folder is outside `~/.n8n-files/`; see step 2 |
| `Missing file: …` | Check `job_file` / `resume_file` in `run-config.json` and the `data_dir` in Settings |
| Command-line runs exit silently while the editor is open | Set `N8N_RUNNERS_BROKER_PORT=5689` for the command-line run (`run_batch.py` does this) |
