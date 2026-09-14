export const BASE_URL =
  import.meta.env.SERVER_URL || "http://localhost:8000";

export const AI_BASE_URL = import.meta.env.VITE_AI_BASE_URL || "http://127.0.0.1:8000";

export const API_PATHS = {
  AUTH: {
    LOGIN: "/api/v1/auth/login",
    REGISTER: "/api/v1/auth/register",
    PROFILE: "/api/v1/auth/profile",
  },

  DASHBOARD: {
    SUMMARY: "/api/v1/summary",
  },
 
  INCOME: {
    CREATE: "/api/v1/income",
    GET_ALL: "/api/v1/income",
    GET_BY_ID: (incomeId) => `/api/v1/income/${incomeId}`,
    UPDATE: (incomeId) => `/api/v1/income/${incomeId}`,
    DELETE: (incomeId) => `/api/v1/income/${incomeId}`,
    DOWNLOAD: "/api/v1/income/download",
  },

  EXPENSE: {
    CREATE: "/api/v1/expense",
    GET_ALL: "/api/v1/expense",
    GET_BY_ID: (expenseId) => `/api/v1/expense/${expenseId}`,
    UPDATE: (expenseId) => `/api/v1/expense/${expenseId}`,
    DELETE: (expenseId) => `/api/v1/expense/${expenseId}`,
    DOWNLOAD: "/api/v1/expense/download",
  },

  TRANSACTIONS: {
    CREATE: "/api/v1/transaction",
    GET_ALL: "/api/v1/transactions",

    GET_BY_ID: (type, id) =>
      `/api/v1/transaction/${type}/${id}`,

    UPDATE: (type, id) =>
      `/api/v1/transaction/${type}/${id}`,

    DELETE: (type, id) =>
      `/api/v1/transaction/${type}/${id}`,

    DOWNLOAD: "/api/v1/transactions/download",
  },
  AI_ASSISTANT: {
    GET_RESPONSE: "/ai/analyze",
  },
};