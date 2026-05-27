const express = require('express');
const { protect } = require('../middleware/auth.middleware');
const { analyzeTransactions } = require('../controllers/ai.controller');

const router = express.Router();

router.post('/analyze', protect, analyzeTransactions);

module.exports = router;