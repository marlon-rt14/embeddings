# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A hands-on learning repo for text embeddings, built as a progression of Jupyter notebooks in `scripts/`
(`1_text_similarity` → `2_semantic_search` → `3_recommendation_systems` → `4_classification` →
`5_querying_and_persistence`). `scripts/main.ipynb` is the original scratch notebook the numbered ones were
extracted from. There is no application, no build step, no test suite, and no linter.

## Critical: it uses Gemini, not OpenAI

Despite the repo name, **all embedding calls go to Gemini**. The owner has no OpenAI credits and does not
want to pay for them — never switch code to the OpenAI models/endpoint.

Two distinct paths to Gemini coexist:

1. **`scripts/helpers.py` → `EmbeddingClient`** (notebooks 1–4): uses the `openai` SDK pointed at Gemini's
   OpenAI-compatible endpoint `https://generativelanguage.googleapis.com/v1beta/openai/`, with
   `MODEL = "gemini-embedding-001"` and `GEMINI_API_KEY` as the api_key.
2. **ChromaDB's `GoogleGeminiEmbeddingFunction`** (notebook 5): the native Gemini client. It reads
   `GEMINI_API_KEY` from `os.environ` itself — nothing is passed to the constructor, so the env var must
   already be set (notebook 5 does `os.environ["GEMINI_API_KEY"] = api_key` explicitly).

`.env` (gitignored) holds `GEMINI_API_KEY` and an unused `OPENAI_API_KEY`. Every notebook starts with
`load_dotenv()`.

## Notebooks must run with the repo root as CWD

There are no `__init__.py` files — `utils` and `scripts` resolve as namespace packages, and every path is
relative to the repo root:

- imports: `from utils.utils import ...`, `from scripts.helpers import ...`
- data: `read_products()` opens `products.json`; `netflix_titles.csv` and `./chroma_db` also sit at root

So a notebook in `scripts/` only works if the kernel's working directory is the repo root, not
`scripts/`. If imports or file reads fail, that is almost always the cause (in VS Code, set
`jupyter.notebookFileRoot` to `${workspaceFolder}`).

## Commands

```bash
source .venv/bin/activate          # Python 3.13
pip install -r requirements.txt    # plain pip freeze output
pip freeze > requirements.txt      # how the file is regenerated

jupyter lab                        # run from the repo root, never from scripts/
.venv/bin/python -m script         # for one-off checks, also from the repo root
```

### Chroma server

Notebook 5 uses embedded mode (`chromadb.PersistentClient(path="./chroma_db")`), so no server is needed
to run it. The server is only for inspecting the store or sharing it across processes:

```bash
chroma run --path ./chroma_db              # serves http://localhost:8000
chroma run --path ./chroma_db --port 8001  # if 8000 is taken
curl http://localhost:8000/api/v2/heartbeat

chroma browse netflix_titles --local --path ./chroma_db   # TUI collection browser
```

To talk to it from a notebook, swap the client — the rest of the collection API is identical:

```python
client = chromadb.HttpClient(host="localhost", port=8000)
```

**Don't run the server and a `PersistentClient` against `./chroma_db` at the same time.** Two processes
holding the same persistence directory fight over the SQLite file. Pick one: embedded *or* server.

## Gotchas

- `EmbeddingClient.create_embeddings` catches its exceptions and only *prints* them, returning `None`.
  A failed call therefore surfaces later as a confusing `TypeError` on the result, not as an API error.
- It always returns a list. Passing a single string still yields `[embedding]`, hence the `[0]` in the
  notebooks.
- `chroma_db/` is a local Chroma store that is untracked but *not* in `.gitignore` — don't commit it by
  accident. Notebook 5 uses `get_or_create_collection`, so re-runs reuse existing data rather than re-embed.
- Notebook markdown is in English; inline code comments are sometimes in Spanish. Match the surrounding
  cell rather than normalizing.
