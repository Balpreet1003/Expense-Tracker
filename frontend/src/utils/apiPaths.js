export const BASE_URL = "https://expense-tracker-ten-zeta-17.vercel.app";
//export const BASE_URL = "http://localhost:8000";

// utils/apiPaths.js
export const API_PATHS = {
      AUTH: {
            LOGIN: "/api/v1/auth/login",
            REGISTER: "/api/v1/auth/register",
            GET_USER_INFO: "/api/v1/auth/getUser",
      },
      USER: {
            GET_USER_INFO: "/api/v1/auth/getUser",
      },
      DASHBOARD: {
            GET_DASHBOARD_DATA: "/api/v1/dashboard",
      },
      INCOME: {
            DOWNLOAD_INCOME: "/api/v1/income/download-income",
      },
      EXPENSE: {
            DOWNLOAD_EXPENSE: "/api/v1/expense/download",
      },
      TRANSACTIONS: {
            ADD_TRANSACTION: "/api/v1/transaction/add",
            GET_ALL_TRANSACTIONS: "/api/v1/transaction/get",
            DELETE_TRANSACTION: (transactionId) => `/api/v1/transaction/${transactionId}`,
            DOWNLOAD_TRANSACTIONS: "/api/v1/transaction/download",
      },
      IMAGE: {
            UPLOAD_IMAGE: "/api/v1/auth/upload-image",
      },
};
