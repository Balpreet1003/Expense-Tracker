const { query } = require('../config/db');
const {
      getCachedJson,
      setCachedJson,
      deleteByPattern,
} = require('./redis.service');

const CACHE_TTL_SECONDS = 60 * 60 * 24;

const formatMonth = (value) => {
      if (!value) {
            return null;
      }

      const date = value instanceof Date ? value : new Date(value);

      if (Number.isNaN(date.getTime())) {
            return null;
      }

      return date.toISOString().slice(0, 7);
};

const toNumber = (value) => Number(value || 0);

const normalizeMonthKey = (value = new Date()) => {
      if (typeof value === 'string' && /^\d{4}-\d{2}$/.test(value)) {
            return value;
      }

      const date = value instanceof Date ? value : new Date(value);

      if (Number.isNaN(date.getTime())) {
            return new Date().toISOString().slice(0, 7);
      }

      return date.toISOString().slice(0, 7);
};

const getMonthStart = (monthKey) => new Date(`${monthKey}-01T00:00:00.000Z`);

const getMonthlyFinancialSummary = async (userId, month = new Date()) => {
      const monthKey = normalizeMonthKey(month);
      const cacheKey = `summary:${userId}:${monthKey}`;

      const cachedSummary = await getCachedJson(cacheKey);

      if (cachedSummary) {
            return cachedSummary;
      }

      const result = await query(
            `SELECT month, total_income, total_expense
             FROM monthly_financial_summary
             WHERE user_id = $1
               AND month = DATE_TRUNC('month', $2::timestamptz)
             LIMIT 1`,
            [userId, getMonthStart(monthKey)]
      );

      const summary = result.rows[0]
            ? {
                  month: formatMonth(result.rows[0].month),
                  income: toNumber(result.rows[0].total_income),
                  expense: toNumber(result.rows[0].total_expense),
                  balance: toNumber(result.rows[0].total_income) - toNumber(result.rows[0].total_expense),
            }
            : {
                  month: monthKey,
                  income: 0,
                  expense: 0,
                  balance: 0,
            };

      await setCachedJson(cacheKey, summary, CACHE_TTL_SECONDS);

      return summary;
};

const getCategorySummary = async (userId, month = null) => {
      const monthKey = normalizeMonthKey(month || new Date());
      const cacheKey = `categories:${userId}:${monthKey}`;

      const cachedSummary = await getCachedJson(cacheKey);

      if (cachedSummary) {
            return cachedSummary;
      }

      const result = await query(
            `SELECT month, category, total_amount
             FROM category_summary
             WHERE user_id = $1
               AND month = DATE_TRUNC('month', $2::timestamptz)
             ORDER BY total_amount DESC, category ASC`,
            [userId, getMonthStart(monthKey)]
      );

      const summary = result.rows.map((row) => ({
            month: formatMonth(row.month),
            category: row.category,
            amount: toNumber(row.total_amount),
      }));

      await setCachedJson(cacheKey, summary, CACHE_TTL_SECONDS);

      return summary;
};

const getCardSpendingSummary = async (userId) => {
      const result = await query(
            `SELECT s.card_id,
                    c.card_name,
                    s.total_spent
             FROM card_spending_summary s
             LEFT JOIN cards c ON c.id = s.card_id
             WHERE s.user_id = $1
             ORDER BY s.total_spent DESC, s.card_id ASC`,
            [userId]
      );

      return result.rows.map((row) => ({
            cardId: row.card_id,
            cardName: row.card_name || `Card ${row.card_id}`,
            totalSpent: toNumber(row.total_spent),
      }));
};

const getFinancialAnalyticsSnapshot = async (userId) => {
      const [monthlySummary, categorySummary, cardSpendingSummary] = await Promise.all([
            getMonthlyFinancialSummary(userId),
            getCategorySummary(userId),
            getCardSpendingSummary(userId),
      ]);

      const currentMonth = monthlySummary[0] || {
            month: normalizeMonthKey(new Date()),
            income: 0,
            expense: 0,
            balance: 0,
      };

      return {
            currentMonth,
            monthlySummary,
            categorySummary,
            cardSpendingSummary,
      };
};

const invalidateUserAnalyticsCache = async (userId) => {
      await Promise.all([
            deleteByPattern(`summary:${userId}:*`),
            deleteByPattern(`categories:${userId}:*`),
      ]);
};

module.exports = {
      getMonthlyFinancialSummary,
      getCategorySummary,
      getCardSpendingSummary,
      getFinancialAnalyticsSnapshot,
      invalidateUserAnalyticsCache,
};