
# AI-Powered Expense Tracker – Frontend

A modern and responsive frontend for the **AI-Powered Expense Tracker**, built with React and Vite. It provides an intuitive interface for managing financial data, visualizing spending patterns, and interacting with the AI-powered financial assistant.

<p align="center">

<img src="https://img.shields.io/badge/React-19-blue?logo=react">

<img src="https://img.shields.io/badge/Vite-Build%20Tool-purple?logo=vite">

<img src="https://img.shields.io/badge/Tailwind_CSS-4-blue?logo=tailwindcss">

<img src="https://img.shields.io/badge/Axios-HTTP%20Client-purple">

<img src="https://img.shields.io/badge/Recharts-Data%20Visualization-orange">

</p>

---

## Table of Contents

- [Live Demo](#live-demo)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Security Features](#security-features)
- [Performance Optimizations](#performance-optimizations)

---

## Live Demo

🚀 **Live Application:**  
https://expense-tracker-wjx8.vercel.app/

---

## Features

- Secure login and registration interface with protected application routes
- Interactive dashboard for viewing income, expenses, balance, and recent activity
- Dedicated interfaces for managing income, expenses, transactions, and financial cards
- Interactive charts and visualizations for analyzing financial data
- AI financial assistant interface with responsive and user-friendly interactions

---

## Tech Stack

### Frontend Framework

- React 19
- Vite

### Styling

- Tailwind CSS

### Routing

- React Router DOM

### API Communication

- Axios

### Data Visualization

- Recharts

### Additional Libraries

- React Markdown
- React Icons
- Moment.js
- React Hot Toast
- React Toastify
- Emoji Picker React

### Deployment

- Vercel

---

## System Architecture

```text
                         React + Vite
                               │
                               ▼
                          React Router
                               │
                               ▼
                      Pages and Components
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       Authentication      Dashboard       AI Assistant
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                         Axios Client
                               │
                               ▼
                         REST API Request
                               │
                               ▼
                            Backend
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/Balpreet1003/Expense-Tracker.git
```

Move to the frontend directory:

```bash
cd Expense-Tracker/frontend
```

---

### Install Dependencies

```bash
npm install
```

---

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

---

### Start Development Server

```bash
npm run dev
```

The application will typically run at:

```text
http://localhost:5173
```

---

### Build for Production

Create an optimized production build:

```bash
npm run build
```

---

### Preview Production Build

Preview the production build locally:

```bash
npm run preview
```

---

## Security Features

- Protected routes to prevent unauthorized access to authenticated pages
- JWT-based authentication for secure communication with backend APIs
- Authentication state management for handling user sessions
- Unauthorized request handling and protected API access
- Environment variables for managing frontend configuration securely

---

## Performance Optimizations

- Vite-powered development and optimized production builds
- Reusable and modular component-based architecture
- Client-side routing for faster navigation between application pages
- Efficient API communication using a centralized Axios configuration
- Responsive UI optimized for different screen sizes
