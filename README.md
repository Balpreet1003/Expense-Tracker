# AI-Powered Expense Tracker

An intelligent full-stack personal finance management application that enables users to efficiently manage their income, expenses, transactions, and financial information while leveraging an AI-powered financial assistant for personalized insights.

Unlike traditional expense trackers, this application combines structured financial management and analytics with an AI-powered assistant to generate personalized, data-driven financial insights.

---

## Table of Contents

- [Live Demo](#live-demo)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## Live Demo

### Frontend

https://expense-tracker-wjx8.vercel.app/

### Backend API

https://your-backend-api.vercel.app/

---

## Features

- Secure authentication and personalized user account management
- Income, expense, transaction, and financial card management
- Interactive dashboard with financial analytics and visualizations
- AI-powered financial assistant for personalized, data-driven insights
- Excel export and a responsive user interface for seamless financial management

---

## System Architecture

```text
                              React + Vite
                                    │
                                    ▼
                               React Router
                                    │
                                    ▼
                              User Interface
                                    │
                                    ▼
                              Axios REST API
                                    │
                                    ▼
                                 Backend
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
         Authentication        Finance APIs         AI Assistant
                │                   │                   │
                ▼                   ▼                   ▼
          JWT + bcrypt        PostgreSQL        Analytics + RAG
                                                        │
                              ┌─────────────────────────┴─────────────────────────┐
                              │                                                   │
                              ▼                                                   ▼
                       SQL Analytics                                      Vector Search
                                                                         (pgvector)
                              │                                                   │
                              └─────────────────────────┬─────────────────────────┘
                                                        │
                                                        ▼
                                                   Gemini AI
                                                        │
                                                        ▼
                                             Personalized Response
```

---

## Future Improvements

- Savings goals and advanced budget planning
- AI-powered forecasting and spending predictions
- OCR-based bill scanning and voice-based expense entry
- Multi-currency support and recurring transaction management
- Automated email reports and PDF financial exports

---

## Author

**Balpreet Singh Gill**

GitHub: https://github.com/Balpreet1003

LinkedIn: https://www.linkedin.com/in/balpreet-singh-gill-72374925b/

---

⭐ If you found this project useful, consider giving it a star on GitHub!
