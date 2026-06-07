require("dotenv").config();
const express = require("express");
const cors = require("cors");
const path = require("path");
const { connectDB } = require("./src/config/db");
const authRoutes = require("./src/routes/authRoutes");
const incomeRoutes = require("./src/routes/incomeRoutes");
const expenseRoutes = require("./src/routes/expenseRoutes");
const dashboardRoutes = require("./src/routes/dashboardRoutes");
const transactionRoutes = require("./src/routes/transactionRoutes");
const cardsRoutes = require("./src/routes/cardsRoutes");
const aiRoutes = require("./src/routes/aiRoutes");
const { error } = require("console");

const app = express();

// middleware to handle CORS
// Allow the deployed frontend URL, local dev, and Vercel preview domains.
const allowedOrigins = new Set(
      [
            process.env.FRONTEND_URL || 'http://localhost:5173',
            'https://expense-tracker-wjx8.vercel.app',
            process.env.FRONTEND_URLS,
      ]
            .filter(Boolean)
            .flatMap((value) => value.split(','))
            .map((value) => value.trim())
            .filter(Boolean)
);

const isAllowedOrigin = (origin) => {
      if (allowedOrigins.has(origin)) return true;

      try {
            const url = new URL(origin);
            return url.protocol === 'https:' && /\.vercel\.app$/i.test(url.hostname);
      } catch {
            return false;
      }
};

const corsOptions = {
      origin: (origin, callback) => {
            // Allow requests with no origin (server-to-server, mobile, curl)
            if (!origin) return callback(null, true);
            if (isAllowedOrigin(origin)) return callback(null, true);
            return callback(new Error('CORS policy: Origin not allowed'), false);
      },
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'Accept', 'X-Requested-With'],
      credentials: true,
};

app.use(cors(corsOptions));
app.options(/.*/, cors(corsOptions));

app.use(express.json());

connectDB().catch((err) => {
      console.error('Initial database connection failed:', err);
});

app.use("/api/v1/auth", authRoutes);
app.use("/api/v1/income", incomeRoutes);
app.use("/api/v1/expense", expenseRoutes);
app.use("/api/v1/dashboard", dashboardRoutes); 
app.use("/api/v1/transaction", transactionRoutes);
app.use("/api/v1/cards", cardsRoutes);
app.use("/api/v1/ai", aiRoutes);

//server uploads folder
app.use("/uploads", express.static(path.join(__dirname, "uploads")));  
app.get("/", (req, res) => {
      res.send({
            activestatus: true, 
            error: false,
            message: "Welcome to the Expense Tracker API",
      })
})
 
const PORT = process.env.PORT || 5000;
// console.log(`PORT value is: ${PORT}`);

if (require.main === module && !process.env.VERCEL) {
      app.listen(PORT, () => console.log(`Server is running on port ${PORT}`));
}

module.exports = app;