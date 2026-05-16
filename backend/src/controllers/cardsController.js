const { pool, query } = require('../config/db');
const {
    parseBoolean,
    normalizeCardNumber,
    normalizeCardType,
    parseIntegerId,
    toCardResponse,
} = require('../utils/pgHelpers');

const allowedCardTypes = new Set(['Visa', 'MasterCard', 'AmericanExpress', 'RuPay', 'Other']);

const parseExpiryDate = (value) => {
    if (typeof value !== 'string') {
        return null;
    }

    const trimmed = value.trim();

    if (!/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
        return null;
    }

    return trimmed;
};

const validateCardPayload = (payload, allowPartial = false) => {
    const cardName = typeof payload.cardName === 'string' ? payload.cardName.trim() : '';
    const cardNumber = normalizeCardNumber(payload.cardNumber);
    const cardType = normalizeCardType(payload.cardType);
    const expiryDate = parseExpiryDate(payload.expiryDate);
    const cvv = typeof payload.cvv === 'string' ? payload.cvv.trim() : '';
    const bankName = typeof payload.bankName === 'string' ? payload.bankName.trim() : '';

    if (!allowPartial) {
        if (!cardName || !cardNumber || !cardType || !expiryDate || !cvv || !bankName) {
            return { error: 'All fields are required' };
        }
    }

    if (cardType && !allowedCardTypes.has(cardType)) {
        return { error: 'Invalid card type' };
    }

    if (cardNumber && (cardNumber.length < 12 || cardNumber.length > 19)) {
        return { error: 'Card number must contain 12 to 19 digits' };
    }

    if (cvv && !/^\d{3,4}$/.test(cvv)) {
        return { error: 'CVV must contain 3 or 4 digits' };
    }

    return {
        cardName,
        cardNumber,
        cardType,
        expiryDate,
        cvv,
        bankName,
    };
};

// Add a new card
exports.addCard = async (req, res) => {
    const userId = req.user.id;

    try {
        const normalized = validateCardPayload(req.body);

        if (normalized.error) {
            return res.status(400).json({ message: normalized.error });
        }

        const isDefault = parseBoolean(req.body.isDefault);
        const client = await pool.connect();

        try {
            await client.query('BEGIN');

            if (isDefault) {
                await client.query(
                    `UPDATE cards
                     SET is_default = FALSE
                     WHERE user_id = $1 AND is_default = TRUE`,
                    [userId]
                );
            }

            const result = await client.query(
                `INSERT INTO cards (user_id, card_name, card_number, card_type, expiry_date, cvv, bank_name, is_default)
                 VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                 RETURNING id, user_id, card_name, card_number, card_type, expiry_date, cvv, bank_name, is_default, created_at, updated_at`,
                [
                    userId,
                    normalized.cardName,
                    normalized.cardNumber,
                    normalized.cardType,
                    normalized.expiryDate,
                    normalized.cvv,
                    normalized.bankName,
                    isDefault,
                ]
            );

            await client.query('COMMIT');
            res.status(201).json(toCardResponse(result.rows[0]));
        } catch (error) {
            await client.query('ROLLBACK');

            if (error.code === '23505') {
                return res.status(409).json({ message: 'Card number already exists or default card conflict' });
            }

            throw error;
        } finally {
            client.release();
        }
    } catch (error) {
        res.status(500).json({ message: "Server Error" });
    }
}

// Get all cards for a user
exports.getAllCards = async (req, res) => {
    const userId = req.user.id;

    try {
        const result = await query(
            `SELECT id, user_id, card_name, card_number, card_type, expiry_date, cvv, bank_name, is_default, created_at, updated_at
             FROM cards
             WHERE user_id = $1
             ORDER BY created_at DESC, id DESC`,
            [userId]
        );

        res.json(result.rows.map(toCardResponse));
    } catch (error) {
        res.status(500).json({ message: "Server Error" });
    }
}

// Delete a card by ID
exports.deleteCard = async (req, res) => {
    try {
        const cardId = parseIntegerId(req.params.id);

        if (!cardId) {
            return res.status(400).json({ message: "Invalid card id" });
        }

        const result = await query(
            `DELETE FROM cards
             WHERE id = $1 AND user_id = $2
             RETURNING id`,
            [cardId, req.user.id]
        );

        if (!result.rowCount) {
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
        const cardId = parseIntegerId(req.params.id);

        if (!cardId) {
            return res.status(400).json({ message: "Invalid card id" });
        }

        const existingCardResult = await query(
            `SELECT id, user_id, is_default
             FROM cards
             WHERE id = $1 AND user_id = $2
             LIMIT 1`,
            [cardId, userId]
        );

        if (!existingCardResult.rowCount) {
            return res.status(404).json({ message: "Card not found" });
        }

        const normalized = validateCardPayload(req.body);

        if (normalized.error) {
            return res.status(400).json({ message: normalized.error });
        }

        const hasIsDefault = Object.prototype.hasOwnProperty.call(req.body, 'isDefault');
        const nextIsDefault = hasIsDefault ? parseBoolean(req.body.isDefault) : existingCardResult.rows[0].is_default;
        const client = await pool.connect();

        try {
            await client.query('BEGIN');

            if (nextIsDefault) {
                await client.query(
                    `UPDATE cards
                     SET is_default = FALSE
                     WHERE user_id = $1 AND id <> $2 AND is_default = TRUE`,
                    [userId, cardId]
                );
            }

            const updatedCard = await client.query(
                `UPDATE cards
                 SET card_name = $1,
                     card_number = $2,
                     card_type = $3,
                     expiry_date = $4,
                     cvv = $5,
                     bank_name = $6,
                     is_default = $7
                 WHERE id = $8 AND user_id = $9
                 RETURNING id, user_id, card_name, card_number, card_type, expiry_date, cvv, bank_name, is_default, created_at, updated_at`,
                [
                    normalized.cardName,
                    normalized.cardNumber,
                    normalized.cardType,
                    normalized.expiryDate,
                    normalized.cvv,
                    normalized.bankName,
                    nextIsDefault,
                    cardId,
                    userId,
                ]
            );

            await client.query('COMMIT');
            res.status(200).json(toCardResponse(updatedCard.rows[0]));
        } catch (error) {
            await client.query('ROLLBACK');

            if (error.code === '23505') {
                return res.status(409).json({ message: 'Card number already exists or default card conflict' });
            }

            throw error;
        } finally {
            client.release();
        }
    } catch (error) {
        res.status(500).json({ message: "Server Error" });
    }
}