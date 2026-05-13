const express = require('express');
const { downloadIncomeExcel } = require('../controllers/incomeController');
const { protect } = require('../middleware/authMiddleware');

const router = express.Router();

router.get("/download-income", protect, downloadIncomeExcel);

module.exports = router;