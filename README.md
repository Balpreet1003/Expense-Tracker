# 💰 AI-Powered Expense Tracker

An intelligent full-stack personal finance management application that enables users to efficiently manage their income, expenses, and financial goals while leveraging an AI-powered financial assistant for personalized insights.

Unlike traditional expense trackers, this application combines structured financial analytics with a **Tool-Augmented Retrieval-Augmented Generation (RAG)** pipeline to generate accurate, data-driven financial recommendations.

<p align="center">

<img src="https://img.shields.io/badge/React-19-blue?logo=react">
<img src="https://img.shields.io/badge/Node.js-Express-green?logo=node.js">
<img src="https://img.shields.io/badge/PostgreSQL-Database-blue?logo=postgresql">
<img src="https://img.shields.io/badge/Redis-Cache-red?logo=redis">
<img src="https://img.shields.io/badge/Gemini-AI-orange">
<img src="https://img.shields.io/badge/License-MIT-success">

</p>

## 📚 Table of Contents

- [🚀 Live Demo](#-live-demo)
- [📌 Features](#-features)
  - [🔐 Authentication](#-authentication)
  - [💰 Income Management](#-income-management)
  - [💸 Expense Management](#-expense-management)
  - [📂 Transaction Management](#-transaction-management)
  - [📊 Dashboard](#-dashboard)
  - [📈 Analytics](#-analytics)
  - [🤖 AI Agent Flow](#-ai-agent-flow)
  - [👤 User Profile](#-user-profile)
- [🏗️ Tech Stack](#️-tech-stack)
- [🏛️ System Architecture](#️-system-architecture)
- [📂 Project Structure](#-project-structure)
- [⚙️ Installation](#️-installation)
- [📡 API Endpoints](#-api-endpoints)
- [🔒 Security Features](#-security-features)
- [⚡ Performance Optimizations](#-performance-optimizations)
- [📅 Future Improvements](#-future-improvements)
- [🤝 Contributing](#-contributing)
- [👨‍💻 Author](#-author)

## 🚀 Live Demo

### Frontend
https://expense-tracker-wjx8.vercel.app/

### Backend API
https://your-backend-api.vercel.app/

---

## 📌 Features

### 🔐 Authentication

- Secure User Registration
- User Login
- JWT-based Authentication
- Password Hashing using bcrypt
- Protected Routes
- Persistent Authentication

---

### 💰 Income Management

- Add Income
- Edit Income
- Delete Income
- Categorize Income
- Income History
- Monthly Income Analytics

---

### 💸 Expense Management

- Add Expenses
- Edit Expenses
- Delete Expenses
- Expense Categories
- Monthly Expense Tracking
- Spending Analysis

---

### 📂 Transaction Management

- Complete Transaction History
- Search Transactions
- Filter by Category
- Filter by Date
- Recent Activity

---

### 📊 Dashboard

A centralized dashboard providing a comprehensive overview of the user's financial health.

Includes:

- Current Balance
- Total Income
- Total Expenses
- Monthly Overview
- Recent Transactions
- Income vs Expense
- Category-wise Spending
- Financial Summary

---

### 📈 Analytics

Interactive financial visualizations powered by Recharts.

Available analytics include:

- Monthly Spending Trends
- Income vs Expense Comparison
- Category Breakdown
- Top Spending Categories
- Financial Overview
- Spending Distribution

---

## 🤖 AI Agent Flow

Instead of sending every user query directly to a Large Language Model (LLM), this project implements a **tool-augmented Retrieval-Augmented Generation (RAG) pipeline** that combines structured financial analytics with semantic knowledge retrieval to generate accurate, personalized financial insights.

### Workflow

#### 1. User Query

The user asks a financial question, such as:

- "Where am I spending the most money?"
- "How can I reduce my monthly expenses?"
- "Give me budgeting suggestions."

---

#### 2. Intent Detection

The request is received by the AI Controller and forwarded to the AI Agent.

The AI Agent first determines what the user is asking.

- A **rule-based intent router** handles common financial queries for fast and deterministic classification.
- For ambiguous or complex questions, **Gemini** classifies the intent more accurately.

---

#### 3. Tool Planner

Once the intent is identified, the AI Agent does **not** immediately invoke the LLM.

Instead, the request is passed to a **Tool Planner**, which determines the backend analytics required to answer the user's query.

---

#### 4. Analytics Execution

The planner executes one or more analytics tools depending on the query.

Examples include:

- Financial Overview
- Category Analysis
- Spending Trends
- Top Transactions

Each tool performs optimized SQL queries or reads from materialized views to retrieve structured financial data.

---

#### 5. Semantic Knowledge Retrieval

For queries requiring financial knowledge (such as budgeting strategies or saving advice), the system performs semantic search over a financial knowledge base.

- Financial documents are stored in PostgreSQL.
- Embeddings are generated and stored using **pgvector**.
- The user's query is converted into an embedding.
- A similarity search retrieves the most relevant financial documents.

---

#### 6. Response Generation

The AI Agent combines two sources of information:

- User-specific financial analytics from PostgreSQL
- Financial knowledge retrieved through vector search

This ensures responses are grounded in the user's actual financial data rather than generic AI-generated answers.

---

#### 7. Selective LLM Enhancement

The LLM is used selectively for:

- Intent Classification
- Natural Language Enhancement
- Response Formatting

Calculations and data retrieval remain database-driven, significantly reducing hallucinations.

---

#### 8. Redis Caching

Frequently accessed:

- Knowledge Base Results
- AI Responses

are cached using Redis to improve response time and reduce unnecessary LLM calls.

---

### AI Request Flow

```text
                     User Query
                          │
                          ▼
                 Intent Detection
          (Rule-Based Router / Gemini)
                          │
                          ▼
                    Tool Planner
                          │
         ┌────────────────┴────────────────┐
         │                                 │
         ▼                                 ▼
 Execute Analytics Tools          Vector Search
(SQL & Materialized Views)    (PostgreSQL + pgvector)
         │                                 │
         └────────────────┬────────────────┘
                          ▼
      Merge Analytics + Retrieved Knowledge
                          │
                          ▼
          Optional LLM Enhancement
                          │
                          ▼
      Personalized Financial Response
```

---

### 👤 User Profile

- Update Personal Information
- Upload Profile Picture
- Cloudinary Image Storage

---

## 🏗️ Tech Stack

### Frontend

- React 19
- Vite
- Tailwind CSS
- React Router DOM
- Axios
- Recharts
- React Markdown
- React Hot Toast

---

### Backend

- Node.js
- Express.js
- PostgreSQL
- Redis
- JWT
- bcrypt
- Multer
- Cloudinary

---

### AI Stack

- Gemini API
- Tool-Augmented RAG
- PostgreSQL
- pgvector
- Redis
- Materialized Views
- Prompt Engineering

---

### Deployment

- Frontend → Vercel
- Backend → Vercel
- PostgreSQL
- Redis
- Cloudinary

---

## 🏛️ System Architecture

```text
                        React + Vite
                             │
                             ▼
                     REST API (Axios)
                             │
                             ▼
                     Express Backend
                             │
       ┌─────────────────────┼─────────────────────┐
       │                     │                     │
       ▼                     ▼                     ▼
 Authentication      Finance APIs          AI Agent
       │                     │                     │
       ▼                     ▼                     ▼
 PostgreSQL          Analytics Engine      Tool Planner
                                              │
                            ┌─────────────────┴────────────────┐
                            ▼                                  ▼
                   SQL Analytics                   Vector Search
                            │                      (pgvector)
                            └──────────────┬───────────────┘
                                           ▼
                                     Gemini API
                                           │
                                           ▼
                                 Personalized Response
```

---

## 📂 Project Structure

```text
Expense-Tracker
│
├── frontend
│   ├── public
│   ├── src
│   │   ├── assets
│   │   ├── components
│   │   ├── context
│   │   ├── hooks
│   │   ├── pages
│   │   ├── services
│   │   ├── utils
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   └── package.json
│
├── backend
│   ├── src
│   │   ├── ai
│   │   ├── analytics
│   │   ├── config
│   │   ├── controllers
│   │   ├── middleware
│   │   ├── models
│   │   ├── repositories
│   │   ├── routes
│   │   ├── services
│   │   ├── utils
│   │   └── server.js
│   │
│   └── package.json
│
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/Balpreet1003/Expense-Tracker.git
```

```bash
cd Expense-Tracker
```

---

### Backend Setup

```bash
cd backend
npm install
```

Create a `.env` file.

```env
PORT=5000

DATABASE_URL=your_postgresql_connection_string

JWT_SECRET=your_jwt_secret

GEMINI_API_KEY=your_gemini_api_key

REDIS_URL=your_redis_connection

CLOUDINARY_CLOUD_NAME=your_cloud_name

CLOUDINARY_API_KEY=your_api_key

CLOUDINARY_API_SECRET=your_api_secret

FRONTEND_URL=http://localhost:5173
```

Start Backend

```bash
npm run dev
```

---

### Frontend Setup

```bash
cd frontend

npm install
```

Create a `.env` file

```env
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

Start Frontend

```bash
npm run dev
```

---

## 📡 API Endpoints

### Authentication

```http
POST /api/v1/auth/register

POST /api/v1/auth/login
```

---

### Income

```http
GET    /api/v1/income

POST   /api/v1/income

PUT    /api/v1/income/:id

DELETE /api/v1/income/:id
```

---

### Expense

```http
GET    /api/v1/expense

POST   /api/v1/expense

PUT    /api/v1/expense/:id

DELETE /api/v1/expense/:id
```

---

### Dashboard

```http
GET /api/v1/dashboard
```

---

### Transactions

```http
GET /api/v1/transaction
```

---

### AI Assistant

```http
POST /api/v1/ai/chat
```

---

## 🔒 Security Features

- JWT Authentication
- Password Hashing using bcrypt
- Protected API Routes
- Input Validation
- Environment Variable Management
- Secure File Uploads
- CORS Configuration

---

## ⚡ Performance Optimizations

- Redis Caching
- Materialized Views
- Optimized SQL Queries
- Vector Similarity Search
- Lazy Loading
- Efficient API Design

---

## 📅 Future Improvements

- Budget Planning
- Recurring Transactions
- Savings Goals
- AI Budget Forecasting
- OCR Bill Scanner
- Email Reports
- PDF Export
- Excel Export
- Multi-Currency Support
- Mobile Application
- Voice-based Expense Entry

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Add feature"
```

4. Push your branch

```bash
git push origin feature-name
```

5. Open a Pull Request


---

## 👨‍💻 Author

**Balpreet Singh Gill**

GitHub: https://github.com/Balpreet1003

LinkedIn: https://www.linkedin.com/in/balpreet-singh-gill-72374925b/

---

⭐ If you found this project useful, consider giving it a star on GitHub!
