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

//middleware to handle CORS
// Configure CORS to allow requests from the frontend.
// Use an allowlist and echo the incoming origin when allowed so the
// Access-Control-Allow-Origin header is present for preflight requests.
const allowedOrigins = [
      process.env.FRONTEND_URL || 'http://localhost:5173',
      'https://expense-tracker-wjx8.vercel.app',
];

app.use(
      cors({
            origin: (origin, callback) => {
                  // Allow requests with no origin (server-to-server, mobile, curl)
                  if (!origin) return callback(null, true);
                  if (allowedOrigins.indexOf(origin) !== -1) return callback(null, true);
                  return callback(new Error('CORS policy: Origin not allowed'), false);
            },
            methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            allowedHeaders: ['Content-Type', 'Authorization'],
            credentials: true,
      })
);

app.use(express.json());

connectDB(); 

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
app.listen(PORT, () => console.log(`Server is running on port ${PORT}`));