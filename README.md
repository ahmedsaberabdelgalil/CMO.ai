# CMO.AI — An Intelligent Multi-Agent System for End-to-End Branding and Marketing Automation

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.111-005571?style=for-the-badge&logo=fastapi" />
  <img src="https://img.shields.io/badge/Python-3.11-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/TypeScript-5-007ACC?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=for-the-badge" />
</p>

<p align="center">
  <b>Faculty of Computers and Data Science — Alexandria University</b><br/>
  Intelligent Systems Department &nbsp;|&nbsp; Supervised by Dr. Yasser Fouad &nbsp;|&nbsp; 2025–2026
</p>

---

## Overview

CMO.AI is a full-stack intelligent marketing automation platform that functions as a virtual Chief Marketing Officer for startups and brand-led businesses.

The platform combines a production-grade FastAPI backend, PostgreSQL database, React frontend, and a LangGraph-powered multi-agent AI architecture to automate branding, content generation, campaign planning, media creation, analytics, and marketing strategy generation.

Users can define their brand identity, generate complete marketing plans, create content calendars, produce campaign assets, and receive actionable insights from a unified dashboard.

---

## System Architecture

```text
┌─────────────────────────────────────────────────┐
│             React + TypeScript Frontend          │
│        Vite • Tailwind CSS • ShadCN UI           │
└────────────────────┬────────────────────────────┘
                     │ REST API /api/v1
┌────────────────────▼────────────────────────────┐
│                 FastAPI Backend                  │
│ Routing → Services → SQLAlchemy → PostgreSQL     │
│ JWT Auth • Pydantic v2 • Alembic                 │
└────────────────────┬────────────────────────────┘
                     │ asyncio.to_thread
┌────────────────────▼────────────────────────────┐
│            Multi-Agent Intelligence Layer        │
│ Brand • Calendar • Content • Image • Video       │
│ Analytics • Marketing • Orchestrator             │
│ LangChain • LangGraph • Groq • Cohere • Pinecone │
└─────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend

| Component         | Technology       |
| ----------------- | ---------------- |
| Web Framework     | FastAPI 0.111    |
| Database          | PostgreSQL 16    |
| ORM               | SQLAlchemy 2.0   |
| Migrations        | Alembic 1.13     |
| Validation        | Pydantic v2      |
| Authentication    | JWT + OAuth2     |
| Password Security | bcrypt + passlib |
| File Storage      | Cloudinary       |
| Payments          | Stripe           |
| Server            | Uvicorn          |

### AI & Agent Layer

| Component              | Technology                   |
| ---------------------- | ---------------------------- |
| Primary LLM            | Groq LLaMA 3.3 70B           |
| Agent Orchestration    | LangChain + LangGraph        |
| RAG                    | Cohere Embeddings + Pinecone |
| Image Generation       | Pollinations AI              |
| Marketing Intelligence | LangChain + Groq             |

### Frontend

| Component        | Technology        |
| ---------------- | ----------------- |
| Framework        | React 18          |
| Language         | TypeScript        |
| Build Tool       | Vite              |
| Styling          | Tailwind CSS      |
| UI Library       | ShadCN UI         |
| State Management | React Context API |
| HTTP Client      | Axios             |

---

## AI Agents

The platform includes six specialized agents coordinated through an Orchestrator Agent.

| Agent           | Responsibility                                     |
| --------------- | -------------------------------------------------- |
| Brand Agent     | Brand identity, positioning, audience segmentation |
| Calendar Agent  | Content scheduling and publishing cadence          |
| Content Agent   | Posts, ads, emails, and copywriting                |
| Image Agent     | Creative generation and prompt engineering         |
| Video Agent     | Scripts, storyboards, and creator briefs           |
| Analytics Agent | Performance analysis and recommendations           |
| Marketing Agent | End-to-end marketing strategy generation           |
| Orchestrator    | Routes tasks across agents using LangGraph         |

---

## Project Structure

```text
CMO.ai/
├── alembic/
├── app/
│   ├── api/v1/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   └── agents/
│   └── utils/
├── frontend/
├── requirements.txt
├── alembic.ini
└── README.md
```

---

## Database Design

The platform uses 14 PostgreSQL tables centered around the `brands` entity.

### Core Tables

- users
- team_members
- brands
- marketing_strategies
- content_schedules
- content_items
- campaigns
- campaign_members
- performance_metrics
- assets
- notifications
- plans
- subscriptions
- usage_records

Each marketing strategy, campaign, asset, and metric is associated with a brand, making the brand entity the aggregate root of the domain model.

---

## REST API

All endpoints are versioned under:

```text
/api/v1
```

Authentication uses JWT Bearer Tokens.

### Authentication

```http
POST /auth/register
POST /auth/login
POST /auth/refresh-token
POST /auth/forgot-password
POST /auth/logout
```

### Users

```http
GET  /users/me
PUT  /users/me
PUT  /users/me/password
```

### Brands

```http
POST   /brands
GET    /brands
GET    /brands/{id}
PUT    /brands/{id}
DELETE /brands/{id}
```

### Strategies

```http
POST   /strategies
GET    /strategies
GET    /strategies/{id}
PUT    /strategies/{id}
DELETE /strategies/{id}
PATCH  /strategies/{id}/status
POST   /strategies/{id}/duplicate
```

### Content Calendar

```http
POST   /content-calendar/schedules
GET    /content-calendar/schedules
GET    /content-calendar/calendar
POST   /content-calendar/posts
GET    /content-calendar/posts/{id}
PUT    /content-calendar/posts/{id}
DELETE /content-calendar/posts/{id}
PATCH  /content-calendar/posts/{id}/status
```

### Campaigns

```http
POST   /campaigns
GET    /campaigns
GET    /campaigns/{id}
PUT    /campaigns/{id}
DELETE /campaigns/{id}
PATCH  /campaigns/{id}/status
GET    /campaigns/{id}/performance
```

### Agents

```http
POST /agents/brand/generate
POST /agents/calendar/generate
POST /agents/content/generate
POST /agents/image/generate
POST /agents/video/generate
POST /agents/analytics/generate
POST /agents/marketing/generate
```

---

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Node.js 18+

### Backend Setup

```bash
git clone https://github.com/ahmedsaberabdelgalil/CMO.ai.git

cd CMO.ai

python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env

alembic upgrade head

uvicorn app.main:app --reload
```

Backend URLs:

```text
http://localhost:8000/api/v1
http://localhost:8000/docs
http://localhost:8000/redoc
```

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

## Software Design Patterns

- Service Layer Pattern
- Dependency Injection Pattern
- DTO / Schema Pattern
- Factory Method Pattern
- Strategy Pattern
- Adapter Pattern
- Progressive Async Migration Pattern

---

## Security Features

- JWT Authentication
- Refresh Token Support
- bcrypt Password Hashing
- Ownership-Based Authorization
- CORS Protection
- Environment Variable Secrets
- SQLAlchemy ORM Protection Against SQL Injection

---

## Swagger Authentication

1. Register a new account.
2. Login through `/auth/login`.
3. Click **Authorize**.
4. Paste your access token.
5. Test protected endpoints directly from Swagger UI.

---

### Supervisor

**Dr. Yasser Fouad**

---

## License

This project was developed as a graduation project at Alexandria University, Faculty of Computers and Data Science.

© 2026 All Rights Reserved.
