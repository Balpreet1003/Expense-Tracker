const path = require('path');
const Card = require('../models/Cards');

// Add a new card
exports.addCard = async (req, res) => {
    const userId = req.user.id;

    try {
        const { cardName, cardNumber, cardType, expiryDate, cvv, bankName, isDefault } = req.body;

        // Validation: check for missing fields
        if (!cardName || !cardNumber || !cardType || !expiryDate || !cvv || !bankName) {
            return res.status(400).json({ message: "All fields are required" });
        }

        const newCard = new Card({
            userId,
            cardName,
            cardNumber,
            cardType,
            expiryDate: new Date(expiryDate),
            cvv,
            bankName,
            isDefault
        });

        await newCard.save();
        res.status(200).json(newCard);
    } catch (error) {
        res.status(500).json({ message: "Server Error" });
    }
}

// Get all cards for a user
exports.getAllCards = async (req, res) => {
    const userId = req.user.id;

    try {
        const cards = await Card.find({ userId }).sort({ createdAt: -1 });
        res.json(cards);
    } catch (error) {
        res.status(500).json({ message: "Server Error" });
    }
}

// Delete a card by ID
exports.deleteCard = async (req, res) => {
    try {
        const card = await Card.findByIdAndDelete(req.params.id);
        if (!card) {
            return res.status(404).json({ message: "Card not found" });
        }
        res.status(200).json({ message: "Card Deleted" });
    } catch (error) {
        res.status(500).json({ message: "Server Error" });
    }
}

// Update a card by ID
exports.updateCard = async (req, res) => {
    const userId = req.user.id;

    try {
        const { cardName, cardNumber, cardType, expiryDate, cvv, bankName, isDefault } = req.body;

        // Validation: check for missing fields
        if (!cardName || !cardNumber || !cardType || !expiryDate || !cvv || !bankName) {
            return res.status(400).json({ message: "All fields are required" });
        }

        const updatedCard = await Card.findByIdAndUpdate(
            req.params.id,
            {
                userId,
                cardName,
                cardNumber,
                cardType,
                expiryDate: new Date(expiryDate),
                cvv,
                bankName,
                isDefault
            },
            { new: true }
        );

        if (!updatedCard) {
            return res.status(404).json({ message: "Card not found" });
        }

        res.status(200).json(updatedCard);
    } catch (error) {
        res.status(500).json({ message: "Server Error" });
    }
}