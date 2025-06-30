const express = require('express');

const { downloadExpenseExcel } = require('../controllers/expenseController');
const { protect } = require('../middleware/authMiddleware');

const router = express.Router();

router.get("/download", protect, downloadExpenseExcel);

module.exports = router;