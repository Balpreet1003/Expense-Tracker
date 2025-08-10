const express = require('express');

const {
      addCard,
      getAllCards,
      deleteCard,
      updateCard,
} = require('../controllers/cardsController');

const { protect } = require('../middleware/authMiddleware');

const router = express.Router();

router.post('/add', protect, addCard);
router.get('/get', protect, getAllCards);
router.delete('/:id', protect, deleteCard); 
router.put('/:id', protect, updateCard);

module.exports = router;