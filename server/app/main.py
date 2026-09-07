from fastapi import FastAPI

from app.features.expense.routers.router import router as expense_router
from app.features.auth.routes.router import router as auth_router

app = FastAPI()

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