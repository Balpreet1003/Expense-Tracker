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
- [🏗️ Tech Stack](#️-tech-stack)
- [🏛️ System Architecture](#️-system-architecture)
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

### 🎨 Frontend

- Secure User Authentication (Login & Registration)
- Interactive Dashboard with Financial Overview
- Income & Expense Management
- Transaction History with Search & Filters
- Category-wise Expense Tracking
- Responsive UI built with React and Tailwind CSS
- Interactive Charts and Financial Visualizations
- Profile Management with Image Upload
- Real-time Toast Notifications

---

### ⚙️ Backend

- RESTful APIs built with Express.js
- JWT-based Authentication & Authorization
- Password Hashing using bcrypt
- PostgreSQL Database Integration
- Optimized SQL Queries & Materialized Views
- Cloudinary Integration for Profile Image Storage
- Modular MVC Architecture
- Input Validation & Error Handling
- Redis Caching for Improved Performance

---

### 🤖 AI Agent

- Tool-Augmented Retrieval-Augmented Generation (RAG) Pipeline
- Rule-Based + LLM-powered Intent Detection
- Intelligent Tool Planning for Analytics Execution
- SQL-based Financial Analytics
- Semantic Search using PostgreSQL + pgvector
- Personalized Financial Insights based on User Data
- Financial Knowledge Base Retrieval
- Redis Caching for AI Responses
- Grounded Responses with Reduced Hallucinations

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

- Savings Goals
- AI Budget Forecasting
- OCR Bill Scanner
- Email Reports
- PDF Export
- Multi-Currency Support
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
