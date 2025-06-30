const express = require('express');

const {
      addTransaction,
      getAllTransaction,
      deleteTransaction,
      downloadTransactionExcel,
} = require('../controllers/transactionController');

const {protect} = require('../middleware/authMiddleware');

const router = express.Router();

router.post('/add', protect, addTransaction);
router.get('/get', protect, getAllTransaction);
router.get("/download", protect, downloadTransactionExcel);
router.delete('/:id', protect, deleteTransaction);

module.exports = router;