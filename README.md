# Advanced Python — Engineering & Backend Development Lab

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend_Labs-009688?logo=fastapi&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-F37626?logo=jupyter&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Hands--on-2496ED?logo=docker&logoColor=white)

A hands-on collection of **Python programming notes, coding exercises, FastAPI experiments, and Docker labs**. This repository documents my progression from core Python fundamentals to writing readable, efficient, asynchronous backend services.

Rather than being a single deployable application, this is a **learning and experimentation workspace**: notebooks cover language concepts and problem solving, while small API projects explore practical backend patterns.

## Contents

- [What you'll find](#what-youll-find)
- [Repository structure](#repository-structure)
- [Learning path](#learning-path)
- [Getting started](#getting-started)
- [FastAPI labs](#fastapi-labs)
- [Dockerized Finance AI demo](#dockerized-finance-ai-demo)
- [Engineering concepts practiced](#engineering-concepts-practiced)
- [Project status and roadmap](#project-status-and-roadmap)
- [Author](#author)

## What you'll find

| Area | Focus |
| --- | --- |
| **Python foundations** | Strings, lists, tuples, sets, dictionaries, and variable storage |
| **Advanced Python** | Collections, functions, decorators, object-oriented programming, and advanced OOP |
| **DSA and coding practice** | Array and string exercises, LeetCode-style problems, and CodeWars practice |
| **FastAPI** | Request/response models, validation, endpoints, dependency injection, middleware, and error handling |
| **Async Python** | `async`/`await`, `asyncio.gather`, timeouts, semaphores, and concurrent I/O simulations |
| **Docker** | Container fundamentals, Dockerfiles, and multi-service development with Compose |
| **Finance AI demos** | Small, mock-backed API examples illustrating finance-oriented workflows |

## Repository structure

```text
Advanced_python/
├── Advanced/
│   ├── Basics/                 # Foundational Python notebooks
│   ├── 1_Lists.ipynb
│   ├── 2_Tuples.ipynb
│   ├── 3_Dictionaries.ipynb
│   ├── 4_Sets.ipynb
│   ├── 5_Strings.ipynb
│   ├── 6_Collections.ipynb
│   ├── 7_Functions.ipynb
│   ├── 8_Decorators.ipynb
│   ├── 9_OOP.ipynb
│   └── 10_Adv_OOP.ipynb
├── CodeWars/
│   ├── LeetCode.ipynb
│   ├── p1.ipynb
│   └── practice_DSA_01.ipynb
├── DSA/
│   ├── Array.ipynb
│   ├── Strings.ipynb
│   └── Practical.ipynb         # Currently empty
├── Docker/
│   └── Module_1.ipynb
├── FastAPI/
│   ├── Basic_concept.ipynb
│   ├── Module1.ipynb
│   ├── Module2.ipynb
│   ├── Module3.ipynb
│   ├── Module4.ipynb
│   ├── main.py
│   ├── ai-finance-api/
│   │   └── main.py
│   ├── fastapi-async-lab/
│   │   ├── main.py
│   │   └── requirements.txt    # Currently empty
│   └── fastapi-masterclass/
│       └── main.py
├── Finance_AI/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── Dockerfile
│   ├── compose.yaml
│   └── requirements.txt
└── README.md
```

> Some directories also contain generated Python `__pycache__` files. These are not required for running the examples.

## Learning path

### 1. Core Python

Start with [`Advanced/Basics`](Advanced/Basics), then continue into the numbered notebooks under [`Advanced/`](Advanced/). Topics include collection operations, functions, decorators, classes, inheritance, and other OOP concepts.

### 2. Problem solving and DSA

Explore [`DSA/`](DSA/) for array and string practice, and [`CodeWars/`](CodeWars/) for additional coding challenges and LeetCode exercises. The emphasis is on building problem-solving fluency with Python's built-in data structures.

### 3. Backend development

Move into [`FastAPI/`](FastAPI/) to practice HTTP endpoints, Pydantic validation, structured responses, asynchronous execution, and API design.

### 4. Containers and local services

Use [`Docker/`](Docker/) for container notes and [`Finance_AI/`](Finance_AI/) for a minimal FastAPI service packaged with Docker and a Compose environment containing PostgreSQL, Qdrant, and Redis.

## Getting started

### Prerequisites

- Python **3.12 or newer** (recommended for the examples)
- Git
- JupyterLab or Jupyter Notebook for `.ipynb` files
- Docker Desktop or Docker Engine with Compose for the container lab

### Clone and create an environment

```bash
git clone https://github.com/venkatpachala/Advanced_python.git
cd Advanced_python
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

For notebooks:

```bash
python -m pip install --upgrade pip
python -m pip install jupyterlab ipykernel
python -m ipykernel install --user --name advanced-python --display-name "Python (Advanced Python)"
jupyter lab
```

Choose the **Python (Advanced Python)** kernel and open any notebook. Notebook-specific dependencies may need to be installed separately; this repository does not currently provide a single consolidated requirements file for all notebooks.

## FastAPI labs

These are independent examples, not one combined service. Install the API dependencies:

```bash
python -m pip install fastapi uvicorn
```

### Async invoice analysis lab

[`FastAPI/fastapi-async-lab/main.py`](FastAPI/fastapi-async-lab/main.py) simulates fetching vendor details, payment history, and policy information concurrently, then generating an answer from that context.

From the repository root:

```bash
cd FastAPI/fastapi-async-lab
uvicorn main:app --reload
```

In a second terminal:

```bash
curl -X POST "http://127.0.0.1:8000/invoices/101/analyze" \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the payment terms?"}'
```

In **PowerShell**, use `curl.exe` on one line or use `Invoke-RestMethod`:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/invoices/101/analyze -Method Post -ContentType 'application/json' -Body '{"question":"What are the payment terms?"}'
```

The example uses simulated data and sleeps; it does not call a real invoice system or LLM.

### AI Finance Assistant API

[`FastAPI/ai-finance-api/main.py`](FastAPI/ai-finance-api/main.py) demonstrates an API flow with:

- Pydantic request and response schemas
- Concurrent mock retrieval and customer lookups
- Request deadlines and an LLM concurrency semaphore
- Correlation IDs, middleware timing logs, and HTTP error handling
- Source citation fields returned in the response

Run it independently:

```bash
cd FastAPI/ai-finance-api
uvicorn main:app --reload
```

Example request:

```json
{
  "query": "How long do eligible refunds take?",
  "user_id": "demo-user",
  "session_id": "demo-session"
}
```

Send it to `POST /ask`, or use the interactive API documentation at **http://127.0.0.1:8000/docs**.

**Note:** Retrieval, customer data, and LLM generation are currently mocked. The returned answer is a demonstration of service orchestration, not a live RAG or production AI integration.

## Dockerized Finance AI demo

[`Finance_AI/`](Finance_AI/) contains a minimal FastAPI application with a health endpoint and a placeholder `/agent` endpoint. Its Docker Compose setup also starts PostgreSQL, Qdrant, and Redis for local infrastructure experimentation.

From the repository root:

```bash
cd Finance_AI
docker compose up --build
```

Once running, open **http://127.0.0.1:8000/docs** or test:

```bash
curl http://127.0.0.1:8000/health
```

To stop the services:

```bash
docker compose down
```

To delete the Compose-managed volumes as well (this removes persisted local service data):

```bash
docker compose down -v
```

**Current scope:** The `/agent` endpoint returns a placeholder response. PostgreSQL, Qdrant, and Redis are declared in Compose but are **not yet integrated into the application's request logic**. The Compose credentials are development examples and must be replaced before any deployment outside a trusted local environment.

## Engineering concepts practiced

The practical API examples explore important building blocks for Python backend and AI application development:

| Concept | Where it appears | Why it matters |
| --- | --- | --- |
| `async` / `await` | FastAPI labs | Non-blocking handling of I/O-oriented work |
| `asyncio.gather()` | Invoice analysis, finance API | Execute independent asynchronous operations concurrently |
| `asyncio.Semaphore` | FastAPI labs | Bound concurrent work and protect constrained resources |
| `asyncio.timeout()` | FastAPI labs | Impose deadlines on async workflows |
| Pydantic models | FastAPI and Finance AI | Validate API inputs and shape responses |
| Middleware and request IDs | AI Finance Assistant API | Support request tracing and diagnostics |
| Dockerfile and Compose | Finance AI | Package an API and run local supporting services |

## Project status and roadmap

This repository is a **work in progress** and is intended for learning, experimentation, and interview preparation. Some notebooks contain exploratory code, some files are empty placeholders, and some APIs use mocked dependencies.

## Author

**Venkat Pachala**  
GitHub: [@venkatpachala](https://github.com/venkatpachala)

---

*Built through hands-on practice — from Python language fundamentals to backend engineering patterns.*
