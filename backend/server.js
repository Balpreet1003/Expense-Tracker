require("dotenv").config();
const express = require("express");
const cors = require("cors");
const path = require("path");
const connectDB = require("./config/db");
const authRoutes = require("./routes/authRoutes");
const incomeRoutes = require("./routes/incomeRoutes");
const expenseRoutes = require("./routes/expenseRoutes");
const dashboardRoutes = require("./routes/dashboardRoutes");
const transactionRoutes = require("./routes/transactionRoutes");
const { error } = require("console");

const app = express();

//middleware to handle CORS
app.use(
      cors({
            origin: [
                "http://localhost:5173", // for local development
                "https://expense-tracker-wjx8.vercel.app", // <-- your frontend production URL
                "https://expense-tracker-ten-zeta-17.vercel.app"
            ],
            methods: ["GET", "POST", "PUT", "DELETE"],
            allowedHeaders: [ "Content-Type", "Authorization" ],
            credentials: true
      }) 
);
   
app.use(express.json());

connectDB(); 

app.use("/api/v1/auth", authRoutes);
app.use("/api/v1/income", incomeRoutes);
app.use("/api/v1/expense", expenseRoutes);
app.use("/api/v1/dashboard", dashboardRoutes); 
app.use("/api/v1/transaction", transactionRoutes);

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
app.listen(PORT, () => console.log(`Server is running on port ${PORT}`));