import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.features.auth.routes.router import router as auth_router
from app.features.income.routers.router import router as income_router
from app.features.expense.routers.router import router as expense_router
from app.features.transactions.routers.router import router as transaction_router
from app.features.dashboard.routers.router import router as dashboard_router


# Load environment variables from the .env file
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],  # In production, specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Expense Tracker API!"
    }

app.include_router(
    auth_router,
    prefix="/api/v1",
    tags=["Auth"]
)

app.include_router(
    expense_router,
    prefix="/api/v1",
    tags=["Expenses"]
)

app.include_router(
    income_router,
    prefix="/api/v1",
    tags=["Incomes"]
)

app.include_router(
    transaction_router,
    prefix="/api/v1",
    tags=["Transactions"]
)

app.include_router(
    dashboard_router,
    prefix="/api/v1",
    tags=["Dashboard"]
)