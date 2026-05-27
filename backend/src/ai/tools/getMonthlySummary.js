const { query } = require('../../config/db');
const { getCachedJson, setCachedJson } = require('../../config/redis');
const { normalizeMonthKey, getMonthDate, getPreviousMonthKey } = require('./shared');

const CACHE_TTL_SECONDS = 60 * 60 * 24;

const getMonthlySummary = async ({ userId, month = getPreviousMonthKey(normalizeMonthKey(new Date())) }) => {
      const monthKey = normalizeMonthKey(month);
      const cacheKey = `summary:${userId}:${monthKey}`;

      const cachedSummary = await getCachedJson(cacheKey);

      if (cachedSummary) {
            return {
                  income: Number(cachedSummary.income || 0),
                  expense: Number(cachedSummary.expense || 0),
            };
      }

      const result = await query(
            `SELECT COALESCE(total_income, 0) AS income,
                    COALESCE(total_expense, 0) AS expense
             FROM monthly_financial_summary
             WHERE user_id = $1
               AND month = DATE_TRUNC('month', $2::timestamptz)
             LIMIT 1`,
            [userId, getMonthDate(monthKey)]
      );

      const summary = {
            income: Number(result.rows[0]?.income || 0),
            expense: Number(result.rows[0]?.expense || 0),
      };

      await setCachedJson(cacheKey, summary, CACHE_TTL_SECONDS);

      return summary;
};

module.exports = {
      name: 'getMonthlySummary',
      description: 'How much did I spend last month?',
      getMonthlySummary,
};