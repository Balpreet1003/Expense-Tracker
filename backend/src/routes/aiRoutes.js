const express = require('express');
const { protect } = require('../middleware/authMiddleware');
const { analyzeTransactions } = require('../controllers/aiController');

const router = express.Router();

router.post('/analyze', protect, analyzeTransactions);

module.exports = router;