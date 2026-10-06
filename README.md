# clinical-evidence-rag

RAG-based clinical decision support assistant with verified citations.

This is our capstone project. The idea of our project is that when a clinician asks a medical question, the system searches a corpus of clinical evidence, and the LLM gives an answer **with citations**. Every citation is checked, so the user can see where each claim comes from and whether the source really supports it.

> **This project is for research and education only. It must not be used to make real clinical decisions.**

## How it works

The pipeline has these steps:

1. **Query expansion (UMLS)**: we expand the user's question with medical synonyms and concepts from UMLS, so the search finds more relevant documents.
2. **Retrieval (BM25 + pgvector)**: hybrid search: BM25 for keywords and pgvector (PostgreSQL) for semantic search with embeddings.
3. **Reranking**: n we reorder the retrieved passages and keep only the most relevant ones.
4. **Generation (LLM)**: the LLM writes the answer using only those passages and adds a citation ID to each claim.
5. **Citation-ID validation**: we check that every citation ID exists and points to a real passage that was retrieved. No invented citations.
6. **Claim-passage alignment (NLI)**: an NLI model checks whether the passage really supports the claim. If it does not, the claim is flagged.

## Data sources

| Source            | Use                                               | Status                        |
| ----------------- | ------------------------------------------------- | ----------------------------- |
| Clinical evidence | the corpus that the retrieval step searches       | to be decided (TBD)           |
| UMLS (NLM)        | medical synonyms and concepts for query expansion | accessed through the UMLS API |

We will update this table once we choose the evidence corpus.

## Tech stack

| Part               | Technology                              |
| ------------------ | --------------------------------------- |
| Backend            | Python 3.12, FastAPI, Uvicorn, Pydantic |
| Frontend           | React 19, Vite                          |
| Database           | PostgreSQL with pgvector                |
| LLM                | OpenAI API                              |
| Medical vocabulary | UMLS API                                |

## Repository structure

```
clinical-evidence-rag/
├── backend/            # FastAPI app and RAG pipeline
│   ├── app/
│   └── requirements.txt
├── frontend/           # React + Vite user interface
├── eval/               # benchmark questions, metrics code and results
├── scripts/            # helper scripts for setup and data loading
├── docs/               # documentation, notes, costs and decisions
├── .github/            # issue templates
├── .env.example        # example of environment variables
├── .pre-commit-config.yaml  # checks that run before every commit
└── ruff.toml           # Python lint and format settings
```

## Setup

What you need:

- Git, Python 3.12 and Node.js 22 (the guides install them)
- Keys for OpenAI and UMLS, and a `DATABASE_URL` (PostgreSQL with pgvector). You can start the app without them.

### macOS

**1. Install the tools.** You need [Homebrew](https://brew.sh) first.

```bash
xcode-select --install
brew install python@3.12 node@22
brew link --force --overwrite node@22
```

Open a new terminal and confirm: `python3.12 --version`, `node --version` (must start with `v22`) and `git --version`.

**2. Get the code and your local settings.**

```bash
git clone https://github.com/capstone-group-l/clinical-evidence-rag.git
cd clinical-evidence-rag
cp .env.example .env
```

**3. Backend.**

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**4. Frontend.** In a second terminal, from the repository root:

```bash
cd frontend
npm install
npm run dev
```

### Windows

Use PowerShell or VS Code terminal:

**1. Install the tools.**

```powershell
winget install Git.Git
winget install Python.Python.3.12
winget install OpenJS.NodeJS.22
```

Close PowerShell, open it again and confirm: `py -3.12 --version`, `node --version` (must start with `v22`) and `git --version`.

**2. Get the code and your local settings.**

```powershell
git clone https://github.com/capstone-group-l/clinical-evidence-rag.git
cd clinical-evidence-rag
copy .env.example .env
```

**3. Backend.**

```powershell
cd backend
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If the activation fails with "running scripts is disabled on this system", allow local scripts for your user once, then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**4. Frontend.** In a second PowerShell window, from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

### After setup (both systems)

- Open http://localhost:5173 to see the frontend.
- `(.venv)` at the start of the prompt means the virtual environment is active. A new terminal starts without it, so activate it again before running backend commands.
- Fill in the empty values in `.env` as you get your keys. Never commit `.env`.

| Variable         | What it is                                                   |
| ---------------- | ------------------------------------------------------------ |
| `OPENAI_API_KEY` | your key for the OpenAI API                                  |
| `UMLS_API_KEY`   | your key for the UMLS API                                    |
| `DATABASE_URL`   | the connection string of your PostgreSQL database            |
| `CORS_ORIGINS`   | the URL of the frontend (default is `http://localhost:5173`) |

When the API entry point is ready, start it from `backend/` with the venv active:

```bash
uvicorn app.main:app --reload
```

Other frontend commands, from `frontend/`:

```bash
npm run build         # create the production build
npm run lint          # check the code with ESLint
npm run format        # format the code with Prettier
npm run format:check  # check the formatting without changing files
npm run preview       # preview the production build locally
```

## Development tools (linting, formatting and pre-commit)

We use [pre-commit](https://pre-commit.com) to check the code automatically every time you run `git commit`. The checks are listed in `.pre-commit-config.yaml`:

| Check             | What it does                                                                           |
| ----------------- | -------------------------------------------------------------------------------------- |
| File hygiene      | removes trailing spaces, fixes line endings, checks YAML/TOML/JSON, finds private keys |
| Ruff              | lints and formats the Python code (settings in `ruff.toml`)                            |
| Prettier + ESLint | formats and lints the frontend code (settings in `frontend/`)                          |

If a check fails, the commit is stopped.

Do this setup **once**, after the steps above. Run the commands from the repository root.

### macOS

```bash
source backend/.venv/bin/activate
pip install -r backend/requirements-dev.txt
npm --prefix frontend install
pre-commit install
```

### Windows

```powershell
backend\.venv\Scripts\Activate.ps1
pip install -r backend\requirements-dev.txt
npm --prefix frontend install
pre-commit install
```

`requirements-dev.txt` installs everything in `requirements.txt` plus the development tools (pre-commit, Ruff, pytest and httpx). The `npm install` step is needed because the frontend checks use the ESLint and Prettier from `frontend/node_modules`.

Optional: run all the checks on every file once, to see the current state of the repository:

```bash
pre-commit run --all-files
```

Useful commands (with the venv active):

```bash
pre-commit run                # run the checks on your staged files without committing
pre-commit run --all-files    # run the checks on every file
ruff check backend            # lint the Python code
ruff format backend           # format the Python code
pytest                        # run the backend tests (from backend/)
```

## Evaluation

The `eval/` folder will hold the benchmark questions, the metrics code and the results. We use them to measure two things: whether the answers are correct, and whether the citations really support the answers.

## Team

Capstone Group L.
