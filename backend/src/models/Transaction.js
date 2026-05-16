const { pool, query } = require('../config/db');
const {
      parseIntegerId,
      parsePositiveAmount,
      toTransactionResponse,
      toTransactionExcelRow,
} = require('../utils/pgHelpers');

const normalizeTransactionType = (value) => {
      if (typeof value !== 'string') {
            return '';
      }

      return value.trim().toLowerCase();
};

const parseTransactionDate = (value) => {
      if (typeof value !== 'string' && !(value instanceof Date)) {
            return null;
      }

      const date = value instanceof Date ? value : new Date(value);

      if (Number.isNaN(date.getTime())) {
            return null;
      }

      return date;
};

const createTransaction = async ({ userId, icon, type, category, amount, date, cards, description, cardId = null }) => {
      const normalizedType = normalizeTransactionType(type);
      const normalizedAmount = parsePositiveAmount(amount);
      const normalizedDate = parseTransactionDate(date);
      const normalizedCards = typeof cards === 'string' ? cards.trim() : '';
      const normalizedDescription = typeof description === 'string' ? description.trim() : '';
      const parsedCardId = cardId ? parseIntegerId(cardId) : null;

      if (!normalizedType || !['income', 'expense'].includes(normalizedType)) {
            const error = new Error('Transaction type must be income or expense');
            error.statusCode = 400;
            throw error;
      }

      if (!category || normalizedAmount === null || !normalizedDate) {
            const error = new Error('All fields are required');
            error.statusCode = 400;
            throw error;
      }

      const result = await query(
            `INSERT INTO transactions (user_id, card_id, cards, icon, type, category, amount, date, description)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
             RETURNING id, user_id, card_id, cards, icon, type, category, amount, date, description, created_at, updated_at`,
            [userId, parsedCardId, normalizedCards, icon || '', normalizedType, category, normalizedAmount, normalizedDate, normalizedDescription]
      );

      return toTransactionResponse(result.rows[0]);
};

const getTransactionsByUserId = async (userId) => {
      const result = await query(
            `SELECT t.id,
                    t.user_id,
                    t.card_id,
                    t.cards,
                    t.icon,
                    t.type,
                    t.category,
                    t.amount,
                    t.date,
                    t.description,
                    t.created_at,
                    t.updated_at,
                    c.card_name
             FROM transactions t
             LEFT JOIN cards c ON c.id = t.card_id
             WHERE t.user_id = $1
             ORDER BY t.date DESC, t.id DESC`,
            [userId]
      );

      return result.rows.map(toTransactionResponse);
};

const getTransactionsByUserIdAndType = async (userId, transactionType) => {
      const normalizedType = normalizeTransactionType(transactionType);

      const result = await query(
            `SELECT t.id,
                    t.user_id,
                    t.card_id,
                    t.cards,
                    t.icon,
                    t.type,
                    t.category,
                    t.amount,
                    t.date,
                    t.description,
                    t.created_at,
                    t.updated_at,
                    c.card_name
             FROM transactions t
             LEFT JOIN cards c ON c.id = t.card_id
             WHERE t.user_id = $1
               AND LOWER(t.type::text) = $2
             ORDER BY t.date DESC, t.id DESC`,
            [userId, normalizedType]
      );

      return result.rows.map(toTransactionResponse);
};

const deleteTransactionByIdAndUserId = async (transactionId, userId) => {
      const parsedTransactionId = parseIntegerId(transactionId);

      if (!parsedTransactionId) {
            const error = new Error('Invalid transaction id');
            error.statusCode = 400;
            throw error;
      }

      const result = await query(
            `DELETE FROM transactions
             WHERE id = $1 AND user_id = $2
             RETURNING id`,
            [parsedTransactionId, userId]
      );

      return result.rowCount > 0;
};

const getDashboardStatsByUserId = async (userId) => {
      const [summaryResult, recentResult, income60Result, expense30Result] = await Promise.all([
            query(
                  `SELECT
                       COALESCE(SUM(CASE WHEN LOWER(type::text) = 'income' THEN amount ELSE 0 END), 0) AS total_income,
                       COALESCE(SUM(CASE WHEN LOWER(type::text) = 'expense' THEN amount ELSE 0 END), 0) AS total_expense
                   FROM transactions
                   WHERE user_id = $1`,
                  [userId]
            ),
            query(
                  `SELECT t.id,
                          t.user_id,
                          t.card_id,
                          t.cards,
                          t.icon,
                          t.type,
                          t.category,
                          t.amount,
                          t.date,
                          t.description,
                          t.created_at,
                          t.updated_at,
                          c.card_name
                   FROM transactions t
                   LEFT JOIN cards c ON c.id = t.card_id
                   WHERE t.user_id = $1
                   ORDER BY t.date DESC, t.id DESC
                   LIMIT 5`,
                  [userId]
            ),
            query(
                  `SELECT t.id,
                          t.user_id,
                          t.card_id,
                          t.cards,
                          t.icon,
                          t.type,
                          t.category,
                          t.amount,
                          t.date,
                          t.description,
                          t.created_at,
                          t.updated_at,
                          c.card_name
                   FROM transactions t
                   LEFT JOIN cards c ON c.id = t.card_id
                   WHERE t.user_id = $1
                     AND LOWER(t.type::text) = 'income'
                     AND t.date >= NOW() - INTERVAL '60 days'
                   ORDER BY t.date DESC, t.id DESC`,
                  [userId]
            ),
            query(
                  `SELECT t.id,
                          t.user_id,
                          t.card_id,
                          t.cards,
                          t.icon,
                          t.type,
                          t.category,
                          t.amount,
                          t.date,
                          t.description,
                          t.created_at,
                          t.updated_at,
                          c.card_name
                   FROM transactions t
                   LEFT JOIN cards c ON c.id = t.card_id
                   WHERE t.user_id = $1
                     AND LOWER(t.type::text) = 'expense'
                     AND t.date >= NOW() - INTERVAL '30 days'
                   ORDER BY t.date DESC, t.id DESC`,
                  [userId]
            ),
      ]);

      return {
            totalIncome: Number(summaryResult.rows[0]?.total_income || 0),
            totalExpense: Number(summaryResult.rows[0]?.total_expense || 0),
            recentTransactions: recentResult.rows.map(toTransactionResponse),
            last60DaysIncomeTransactions: income60Result.rows.map(toTransactionResponse),
            last30DaysExpenseTransactions: expense30Result.rows.map(toTransactionResponse),
      };
};

const toExcelRows = (rows) => rows.map(toTransactionExcelRow);

module.exports = {
      createTransaction,
      getTransactionsByUserId,
      getTransactionsByUserIdAndType,
      deleteTransactionByIdAndUserId,
      getDashboardStatsByUserId,
      toExcelRows,
};