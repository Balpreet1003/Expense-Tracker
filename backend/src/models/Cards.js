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

const validateCardPayload = (payload) => {
    const cardName = typeof payload.cardName === 'string' ? payload.cardName.trim() : '';
    const cardNumber = normalizeCardNumber(payload.cardNumber);
    const cardType = normalizeCardType(payload.cardType);
    const expiryDate = parseExpiryDate(payload.expiryDate);
    const cvv = typeof payload.cvv === 'string' ? payload.cvv.trim() : '';
    const bankName = typeof payload.bankName === 'string' ? payload.bankName.trim() : '';

    if (!cardName || !cardNumber || !cardType || !expiryDate || !cvv || !bankName) {
        return { error: 'All fields are required' };
    }

    if (!allowedCardTypes.has(cardType)) {
        return { error: 'Invalid card type' };
    }

    if (cardNumber.length < 12 || cardNumber.length > 19) {
        return { error: 'Card number must contain 12 to 19 digits' };
    }

    if (!/^\d{3,4}$/.test(cvv)) {
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

const createCard = async ({ userId, cardName, cardNumber, cardType, expiryDate, cvv, bankName, isDefault }) => {
    const normalized = validateCardPayload({ cardName, cardNumber, cardType, expiryDate, cvv, bankName });

    if (normalized.error) {
        const error = new Error(normalized.error);
        error.statusCode = 400;
        throw error;
    }

    const client = await pool.connect();

    try {
        await client.query('BEGIN');

        if (parseBoolean(isDefault)) {
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
                parseBoolean(isDefault),
            ]
        );

        await client.query('COMMIT');
        return toCardResponse(result.rows[0]);
    } catch (error) {
        await client.query('ROLLBACK');
        throw error;
    } finally {
        client.release();
    }
};

const getCardsByUserId = async (userId) => {
    const result = await query(
        `SELECT id, user_id, card_name, card_number, card_type, expiry_date, cvv, bank_name, is_default, created_at, updated_at
         FROM cards
         WHERE user_id = $1
         ORDER BY created_at DESC, id DESC`,
        [userId]
    );

    return result.rows.map(toCardResponse);
};

const deleteCardByIdAndUserId = async (cardId, userId) => {
    const parsedCardId = parseIntegerId(cardId);

    if (!parsedCardId) {
        const error = new Error('Invalid card id');
        error.statusCode = 400;
        throw error;
    }

    const result = await query(
        `DELETE FROM cards
         WHERE id = $1 AND user_id = $2
         RETURNING id`,
        [parsedCardId, userId]
    );

    return result.rowCount > 0;
};

const updateCardByIdAndUserId = async (cardId, userId, payload) => {
    const parsedCardId = parseIntegerId(cardId);

    if (!parsedCardId) {
        const error = new Error('Invalid card id');
        error.statusCode = 400;
        throw error;
    }

    const normalized = validateCardPayload(payload);

    if (normalized.error) {
        const error = new Error(normalized.error);
        error.statusCode = 400;
        throw error;
    }

    const client = await pool.connect();

    try {
        await client.query('BEGIN');

        if (parseBoolean(payload.isDefault)) {
            await client.query(
                `UPDATE cards
                 SET is_default = FALSE
                 WHERE user_id = $1 AND id <> $2 AND is_default = TRUE`,
                [userId, parsedCardId]
            );
        }

        const result = await client.query(
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
                parseBoolean(payload.isDefault),
                parsedCardId,
                userId,
            ]
        );

        await client.query('COMMIT');
        return result.rows[0] ? toCardResponse(result.rows[0]) : null;
    } catch (error) {
        await client.query('ROLLBACK');
        throw error;
    } finally {
        client.release();
    }
};

module.exports = {
    createCard,
    getCardsByUserId,
    deleteCardByIdAndUserId,
    updateCardByIdAndUserId,
};