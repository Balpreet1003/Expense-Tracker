# AI-Powered Expense Tracker – Backend

A secure and scalable backend for the **AI-Powered Expense Tracker**, built with **FastAPI and Python**. It provides RESTful APIs for user authentication, profile management, income and expense management, transaction handling, dashboard analytics, profile image uploads, and Excel data export.

<p align="center">

<img src="https://img.shields.io/badge/Python-FastAPI-blue?logo=python">

<img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi">

<img src="https://img.shields.io/badge/PostgreSQL-Database-blue?logo=postgresql">

<img src="https://img.shields.io/badge/SQLAlchemy-ORM-red">

<img src="https://img.shields.io/badge/JWT-Authentication-black">

<img src="https://img.shields.io/badge/Cloudinary-Cloud%20Storage-blue">

</p>

---

## Table of Contents

* [Live Demo](#live-demo)
* [Features](#features)
* [Tech Stack](#tech-stack)
* [System Architecture](#system-architecture)
* [Installation](#installation)
* [API Endpoints](#api-endpoints)
* [Security Features](#security-features)
* [Performance Optimizations](#performance-optimizations)

---

## Live Demo

⚙️ **Backend API:**
https://expense-tracker-server-eight-umber.vercel.app/

---

## Features

* RESTful APIs for authentication, user profile management, income, expenses, transactions, and dashboard analytics
* JWT-based authentication and authorization for protected API endpoints
* Secure password hashing using bcrypt
* PostgreSQL database integration using SQLAlchemy ORM
* User profile image upload and cloud storage using Cloudinary
* Create, retrieve, update, and delete income records
* Create, retrieve, update, and delete expense records
* Unified transaction APIs supporting both income and expense records
* Dashboard summary containing total income, total expenses, total balance, recent transactions, and seven-day financial data
* Excel export for income, expense, and transaction records using OpenPyXL
* User-specific data access to ensure users can access only their own financial records
* Database schema management using Alembic migrations
* Request validation using Pydantic
* Automated test suite using Pytest

---

## Tech Stack

### Runtime

* Python 3.13+

### Backend Framework

* FastAPI
* Uvicorn

### Database

* PostgreSQL
* SQLAlchemy
* Psycopg

### Authentication

* JSON Web Token (JWT)
* PyJWT
* bcrypt
* Passlib

### Validation

* Pydantic
* Email Validation

### Cloud Storage

* Cloudinary

### File Handling

* FastAPI UploadFile
* python-multipart

### Data Export

* OpenPyXL
* Excel `.xlsx` generation

### Database Migrations

* Alembic

### API Development

* REST APIs
* FastAPI Dependency Injection
* CORS

### Environment Management

* python-dotenv

### Testing

* Pytest
* Pytest-Cov
* HTTPX

### Deployment

* Vercel

---

## System Architecture

```text
                              Client Application
                                      │
                                      ▼
                              FastAPI Application
                                      │
             ┌────────────────────────┼────────────────────────┐
             │                        │                        │
             ▼                        ▼                        ▼
      Authentication             Finance APIs             Dashboard
             │                        │                        │
             ▼                        │                        ▼
       JWT + bcrypt                  │                 Financial Summary
             │                        │                        │
             └───────────────┬────────┴────────────────────────┘
                             │
                             ▼
                         SQLAlchemy
                             │
                             ▼
                       PostgreSQL
                             │
             ┌───────────────┼────────────────┐
             │               │                │
             ▼               ▼                ▼
           Users           Income           Expenses
                                             │
                                             ▼
                                        Transactions
                             │
                             ▼
                    Excel Export / Cloudinary
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/Balpreet1003/expense-tracker-server.git

cd expense-tracker-server
```

---

### Create Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment.

#### macOS / Linux

```bash
source .venv/bin/activate
```

#### Windows

```bash
.venv\Scripts\activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Environment Variables

Create a `.env` file in the backend root directory.

```env
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256

PORT=8000

CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

DB_URL=your_postgresql_connection_string

DB_TEST_URL=your_test_postgresql_connection_string

GEMINI_API_KEY=your_gemini_api_key

REDIS_URL=your_redis_connection_string

FRONTEND_URL=http://localhost:5173
```

> **Note:** Never commit your `.env` file or expose database credentials, JWT secrets, Cloudinary credentials, Redis credentials, or API keys in a public repository.

---

### Run Database Migrations

The project uses **Alembic** for database schema migrations.

To apply all available migrations:

```bash
alembic upgrade head
```

To create a new migration:

```bash
alembic revision --autogenerate -m "your migration message"
```

Then apply the migration:

```bash
alembic upgrade head
```

---

### Start Development Server

From the project root:

```bash
uvicorn app.main:app --reload
```

The backend will typically run at:

```text
http://localhost:8000
```

---

### API Documentation

FastAPI automatically provides interactive API documentation.

#### Swagger UI

```text
http://localhost:8000/docs
```

#### ReDoc

```text
http://localhost:8000/redoc
```

---

### Start Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## API Endpoints

All API endpoints are prefixed with:

```text
/api/v1
```

---

### Authentication

```text
/api/v1/auth/*
```

Handles:

* User registration
* User login
* Get authenticated user profile
* Update authenticated user profile
* Password updates
* Profile image uploads

#### Register User

```http
POST /api/v1/auth/register
```

Supports:

* Full name
* Email
* Password
* Optional profile image

The registration endpoint uses `multipart/form-data`.

Form fields:

```text
fullName
email
password
profileImage
```

---

#### Login

```http
POST /api/v1/auth/login
```

Authenticates the user and returns:

* User information
* JWT access token

---

#### Get Profile

```http
GET /api/v1/auth/profile
```

Returns the currently authenticated user's profile.

Requires:

```text
Authorization: Bearer <token>
```

---

#### Update Profile

```http
PATCH /api/v1/auth/profile
```

Supports updating:

* Full name
* Password
* Profile image

The user's email address cannot be updated through this endpoint.

Form fields:

```text
fullName
password
profileImage
```

At least one field must be provided.

---

### Dashboard

```text
/api/v1/*
```

#### Get Dashboard Summary

```http
GET /api/v1/summary
```

Provides:

* Total income
* Total expenses
* Total balance
* Recent transactions
* Seven-day income summary
* Seven-day expense summary

The seven-day summaries include the current day and the previous six days. Missing dates are returned with a total amount of `0`.

---

### Income

```text
/api/v1/income/*
```

Handles:

* Create income records
* Retrieve all income records
* Retrieve income by ID
* Update income records
* Delete income records
* Export income records to Excel

#### Add Income

```http
POST /api/v1/income
```

#### Get All Income

```http
GET /api/v1/income
```

#### Get Income by ID

```http
GET /api/v1/income/{income_id}
```

#### Update Income

```http
PATCH /api/v1/income/{income_id}
```

#### Delete Income

```http
DELETE /api/v1/income/{income_id}
```

#### Download Income

```http
GET /api/v1/income/download
```

Returns:

```text
incomes.xlsx
```

---

### Expense

```text
/api/v1/expense/*
```

Handles:

* Create expense records
* Retrieve all expense records
* Retrieve expense by ID
* Update expense records
* Delete expense records
* Export expense records to Excel

#### Add Expense

```http
POST /api/v1/expense
```

#### Get All Expenses

```http
GET /api/v1/expense
```

#### Get Expense by ID

```http
GET /api/v1/expense/{expense_id}
```

#### Update Expense

```http
PATCH /api/v1/expense/{expense_id}
```

#### Delete Expense

```http
DELETE /api/v1/expense/{expense_id}
```

#### Download Expenses

```http
GET /api/v1/expense/download
```

Returns:

```text
expenses.xlsx
```

---

### Transactions

```text
/api/v1/transaction/*
```

Transactions provide a unified API layer over the existing **Income** and **Expense** database models.

Handles:

* Create transactions
* Retrieve transaction history
* Retrieve a transaction by type and ID
* Update transactions
* Delete transactions
* Export transactions to Excel

Supported transaction types:

```text
income
expense
```

#### Add Transaction

```http
POST /api/v1/transaction
```

#### Get All Transactions

```http
GET /api/v1/transactions
```

#### Get Transaction by ID

```http
GET /api/v1/transaction/{transaction_type}/{transaction_id}
```

Example:

```text
/api/v1/transaction/income/10
```

or:

```text
/api/v1/transaction/expense/25
```

#### Update Transaction

```http
PATCH /api/v1/transaction/{transaction_type}/{transaction_id}
```

#### Delete Transaction

```http
DELETE /api/v1/transaction/{transaction_type}/{transaction_id}
```

#### Download Transactions

```http
GET /api/v1/transactions/download
```

Returns:

```text
transactions.xlsx
```

The transaction Excel export contains:

```text
ID
Type
Icon
Amount
Date
Source/Category
Description
```

---

## Security Features

* JWT-based authentication and authorization for protected API access
* Password hashing using bcrypt before storing user credentials
* Authentication dependency to protect private API routes
* User-specific authorization to prevent access to another user's financial data
* Email validation using Pydantic `EmailStr`
* Password validation with minimum length requirements
* Environment variables for sensitive configuration and credentials
* CORS configuration using the configured frontend origin
* Input validation using Pydantic schemas
* Database transaction rollback on failed database operations
* Secure profile image upload through Cloudinary
* Restricted transaction types using validated `income` and `expense` values
* Positive and bounded transaction IDs for transaction endpoints

---

## Performance Optimizations

* SQLAlchemy ORM for structured and reusable database queries
* Database-side aggregation for income and expense dashboard calculations
* SQL `SUM` and `GROUP BY` operations for financial analytics
* Limited database queries for retrieving recent transactions
* Recent transactions are sorted by transaction date and creation time
* Seven-day dashboard data is generated efficiently with missing dates filled using zero values
* Streaming responses are used for Excel file downloads
* Modular feature-based architecture separates routers, schemas, services, and models
* Alembic migrations provide controlled and versioned database schema changes
* User-specific database filtering reduces unnecessary data retrieval
* Pydantic response models provide structured and validated API responses

---

## Project Structure

```text
expense-tracker-server/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── core/
│   │   └── Cloudinary/
│   │       └── cloudinary.py
│   │
│   ├── database/
│   │   ├── session.py
│   │   └── base.py
│   │
│   ├── dependencies/
│   │
│   ├── features/
│   │   │
│   │   ├── auth/
│   │   │   ├── dependencies/
│   │   │   ├── models/
│   │   │   ├── routes/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   └── utils/
│   │   │
│   │   ├── expense/
│   │   │   ├── models/
│   │   │   ├── routers/
│   │   │   ├── schemas/
│   │   │   └── services/
│   │   │
│   │   ├── income/
│   │   │   ├── models/
│   │   │   ├── routers/
│   │   │   ├── schemas/
│   │   │   └── services/
│   │   │
│   │   ├── transactions/
│   │   │   ├── routers/
│   │   │   ├── schemas/
│   │   │   └── services/
│   │   │
│   │   └── dashboard/
│   │       ├── routers/
│   │       ├── schemas/
│   │       └── services/
│   │
│   ├── shared/
│   │
│   └── tests/
│       ├── auth/
│       ├── expenses/
│       ├── incomes/
│       ├── transaction/
│       └── dashboard/
│
├── alembic/
│   ├── env.py
│   └── versions/
│
├── alembic.ini
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## Testing

The project uses **Pytest** for automated testing.

Run the complete test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app
```

Run a specific test file:

```bash
pytest app/tests/auth/test_login.py
```

The test suite covers areas including:

* User registration
* User login
* JWT authentication
* Password handling
* User profile operations
* Expense routes
* Income routes
* Transaction routes
* Dashboard functionality

---

## HTTP Status Codes

The API follows standard HTTP status codes.

| Status Code                 | Meaning                                 | Typical Usage                  |
| --------------------------- | --------------------------------------- | ------------------------------ |
| `200 OK`                    | Request succeeded                       | GET, successful update         |
| `201 Created`               | Resource created                        | POST                           |
| `204 No Content`            | Request succeeded without response body | DELETE                         |
| `400 Bad Request`           | Request is invalid                      | Invalid request or update      |
| `401 Unauthorized`          | Authentication failed                   | Missing or invalid credentials |
| `403 Forbidden`             | Access is not permitted                 | Insufficient permission        |
| `404 Not Found`             | Resource does not exist                 | Resource lookup by ID          |
| `422 Unprocessable Entity`  | Validation failed                       | FastAPI/Pydantic validation    |
| `500 Internal Server Error` | Unexpected server error                 | Unhandled backend exception    |

---

## Deployment

The backend can be deployed as a FastAPI application on **Vercel**.

Before deployment, configure the required environment variables in the deployment platform:

```text
JWT_SECRET_KEY
JWT_ALGORITHM
DB_URL
DB_TEST_URL
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
GEMINI_API_KEY
REDIS_URL
FRONTEND_URL
```

For production deployments:

* Use a production PostgreSQL database
* Use a strong randomly generated JWT secret
* Configure the production frontend URL
* Store all credentials as environment variables
* Do not commit `.env` files
* Run the required Alembic migrations against the production database

---

## License

This project is developed as part of the **AI-Powered Expense Tracker** application.
