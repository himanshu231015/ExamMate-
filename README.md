<<<<<<< HEAD
# RGPV ExamMate — AI-Powered University Exam Preparation Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11.9-3776AB.svg?style=flat&logo=Python&logoColor=white)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.31-D71F00.svg?style=flat&logo=SQLAlchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![SQLite / PostgreSQL](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL--Ready-blue.svg?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/Tests-17%20Passed-brightgreen.svg?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org/)

---

## 📖 1. Project Overview

**RGPV ExamMate** is a production-minded, full-stack major project specifically tailored for B.Tech students under **Rajiv Gandhi Proudyogiki Vishwavidyalaya (RGPV)**, Madhya Pradesh, India.

Students typically lose hours scouring disjointed websites for university syllabi, previous-year question papers (PYQs), topic-wise frequency distributions, and exam-oriented answer schemes. **RGPV ExamMate** consolidates this entire workflow into a single unified academic platform.

### Key Capabilities
- **Academic Context & Syllabus Navigation**: Select University (RGPV), Degree (B.Tech), Branch (CSE, AIML), Academic Scheme (CBGS 2019), and Subject with 5-unit syllabus breakdown.
- **Hybrid PYQ Search Engine**: Combines BM25 keyword matching with academic filters (Subject, Unit, Topic, Year, Exam Session, Marks). Displays verifiable original paper links and match reasons.
- **AI Exam Tutor (RAG with Scope Restriction)**: Restricts responses to the university syllabus and exam preparation. Politely declines out-of-scope non-academic requests. Formats answers into 2-mark, 7-mark, and 14-mark schemes with traceable citations.
- **PDF Ingestion & Review Governance**: Multi-tier governance (Student, Contributor, Authorized Reviewer, Admin) with SHA-256 duplicate detection, file size enforcement, and reviewer approval workflows. Contributors cannot approve their own papers.
- **Historical Exam-Pattern Analytics**: Topic appearance frequency dashboard, marks weighting, and chronological backtesting (Precision@K / Recall@K) to prevent future-paper leakage.
- **Personalized Study Planner**: Distributes topics across available study days with practice tasks and completion tracking.
- **Student Feedback & Error Reporting**: Students report broken links, inaccurate answers, or wrong syllabus mappings to feed the controlled improvement workflow.

---

## 🛠️ 2. Technology Stack

### Backend
- **Framework**: Python 3.11 with FastAPI (asynchronous, high performance)
- **Validation**: Pydantic v2 & Pydantic-Settings
- **ORM & Migrations**: SQLAlchemy 2.0 & Alembic
- **Database**: SQLite (local development zero-config) with PostgreSQL compatibility
- **Security & RBAC**: JWT tokens with Bcrypt password hashing and role-based permissions (`student`, `contributor`, `reviewer`, `admin`)
- **PDF Parsing**: PyMuPDF (`fitz`) with regex question segmentation
- **Search & Retrieval**: BM25 (`rank-bm25`) + Modular RAG Adapter

### Frontend (To be initialized in Phase 5)
- **Framework**: React with Vite
- **Styling**: Tailwind CSS & Lucide Icons
- **State & HTTP**: React Router & Axios

---

## 🚀 3. Windows Setup & Installation Guide

This setup guide is tailored for Windows with Python 3.11 installed.

### Step 1: Clone the Repository
```powershell
git clone <repository_url>
cd RGPV
```

### Step 2: Virtual Environment Setup
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell displays an Execution Policy restriction, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

### Step 3: Install Backend Dependencies
```powershell
.\.venv\Scripts\pip install --upgrade pip
.\.venv\Scripts\pip install -r backend\requirements.txt
```

### Step 4: Environment Configuration
Copy the sample environment file:
```powershell
copy backend\.env.example backend\.env
```

The default `.env` is preconfigured for local offline development (no paid API keys required).

### Step 5: Initialize and Seed Database
Run the automated table creation and sample RGPV academic data seed:
```powershell
$env:PYTHONPATH="backend"
.\.venv\Scripts\python -m app.db.init_db
```

### Step 6: Apply Alembic Migrations
```powershell
$env:PYTHONPATH="backend"
.\.venv\Scripts\alembic upgrade head
```

---

## 🧪 4. Running Automated Tests

Run the full automated test suite (17 tests covering health, auth, academic hierarchy, PYQ search, RAG tutor, reviewer governance, and study planner):

```powershell
$env:PYTHONPATH="backend"
.\.venv\Scripts\pytest backend\tests -v
```

Expected output:
```text
============================= 17 passed in 4.26s ==============================
```

---

## 💻 5. Running the Backend Server

Start the FastAPI development server with hot-reload:

```powershell
$env:PYTHONPATH="backend"
.\.venv\Scripts\uvicorn app.main:app --app-dir backend --reload --port 8000
```

Once started:
- **Interactive Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Interactive Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🔑 6. Pre-Seeded Default Test Accounts

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@rgpvexammate.edu` | `Admin@123` | System oversight, role management, syllabus CRUD, error reports |
| **Reviewer** | `reviewer@rgpvexammate.edu` | `Reviewer@123` | Approve/Reject/Return paper submissions with reason notes |
| **Contributor** | `contributor@rgpvexammate.edu` | `Contrib@123` | Submit question paper PDFs (cannot approve own submissions) |
| **Student** | `student@rgpvexammate.edu` | `Student@123` | Search PYQs, AI exam tutor chat, study planner, feedback |

---

## 📚 7. Pre-Seeded RGPV Academic Data

1. **University**: Rajiv Gandhi Proudyogiki Vishwavidyalaya (RGPV Bhopal, MP)
2. **Degree**: B.Tech (4 Years)
3. **Branches**: Computer Science & Engineering (CSE), Artificial Intelligence & Machine Learning (AIML)
4. **Curriculum Scheme**: CBGS 2019 (Choice Based Grading System)
5. **Verified Subjects**:
   - `CS-301`: Data Structures (Semester 3) — Complete 5 Units, 10 detailed syllabus topics, 3 verified past papers (Dec 2023, June 2023, Dec 2022) with 12 extracted questions (2-, 7-, and 14-marks) and authentic PDF source links.
   - `CS-402`: Analysis & Design of Algorithms (Semester 4) — Units & Master Theorem, 0/1 Knapsack PYQs.

---

## 📂 8. Project Structure

```text
RGPV/
├── backend/
│   ├── alembic/                # Alembic database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── api/v1/             # Modular REST API endpoints
│   │   │   ├── academic.py     # Universities, schemes, subjects, syllabus
│   │   │   ├── analytics.py    # Topic frequencies, chronological backtesting
│   │   │   ├── auth.py         # Registration, login, profile, account deletion
│   │   │   ├── chat.py         # AI Tutor RAG, sessions, citations
│   │   │   ├── feedback.py     # Ratings and error reports
│   │   │   ├── pyqs.py         # BM25 + context question search
│   │   │   ├── study_plans.py  # Personalized study planner
│   │   │   └── submissions.py  # Paper upload and reviewer approval workflow
│   │   ├── core/               # App configuration, database engine, security
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── dependencies.py
│   │   │   └── security.py
│   │   ├── db/                 # Database initialization and authentic RGPV seeds
│   │   │   ├── init_db.py
│   │   │   └── seed_data.py
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── academic.py
│   │   │   ├── audit.py
│   │   │   ├── chat.py
│   │   │   ├── feedback.py
│   │   │   ├── question_paper.py
│   │   │   ├── study_plan.py
│   │   │   ├── submission.py
│   │   │   └── user.py
│   │   ├── schemas/            # Pydantic v2 request & response schemas
│   │   ├── services/           # Core business logic
│   │   │   ├── analytics_service.py # Backtesting and topic analytics
│   │   │   ├── audit_service.py     # Audit trails
│   │   │   ├── pdf_service.py       # PDF parsing & question segmentation
│   │   │   ├── pyq_service.py       # Hybrid BM25 search engine
│   │   │   └── rag_service.py       # Scope restriction & grounded AI answers
│   │   └── main.py             # FastAPI entrypoint with CORS & lifespan
│   ├── data/                   # SQLite database directory (exammate.db)
│   ├── tests/                  # Pytest test suite (17 automated tests)
│   ├── uploads/                # Staged & verified PDF documents
│   ├── .env.example            # Environment variables template
│   ├── pytest.ini              # Pytest configuration
│   └── requirements.txt        # Backend dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # Complete documentation
```

---

## 📌 9. Status of Phases

| Phase | Description | Status |
| :--- | :--- | :---: |
| **Phase 1: Foundation** | Project setup, virtual environment, FastAPI root/health endpoints, git | ✅ **Done** |
| **Phase 2: Database** | Normalized SQLAlchemy models, SQLite & PostgreSQL compatibility, Alembic migrations, RGPV seed data | ✅ **Done** |
| **Phase 3: Syllabus & PYQ Engine** | Document ingestion, PDF extraction, question segmentation, BM25 search, verified source links | ✅ **Done** |
| **Phase 4: RAG Engine & AI Tutor** | Scope classifier, grounding, 2/7/14-mark answers, citation generator, offline adapter | ✅ **Done** |
| **Phase 5: Frontend** | React + Vite, Tailwind CSS, student dashboard, syllabus explorer, chat UI, PYQ search | 🔜 **Next Phase** |
| **Phase 6: Auth & Governance** | RBAC enforcement, contributor upload, reviewer workflow, self-approval prevention | ✅ **Done (Backend)** |
| **Phase 7: Feedback & Improvement** | Error reports, ratings, admin metrics, audit logging | ✅ **Done (Backend)** |
| **Phase 8: Historical Analytics & Planner**| Topic frequency dashboard, chronological backtesting, personalized study planner | ✅ **Done (Backend)** |
| **Phase 9: Testing & Deployment** | Automated pytest suite (17 passed), Dockerization, final documentation | 🟡 **In Progress** |
=======
>>>>>>> 390f49ccf3be47e1223a848f94ab9f8422765981
# ExamMate-
