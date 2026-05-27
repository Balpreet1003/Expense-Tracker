const { query } = require('../../config/db');
const { getCachedJson, setCachedJson } = require('../../config/redis');
const { normalizeMonthKey, getMonthDate, getPreviousMonthKey } = require('./shared');

const CACHE_TTL_SECONDS = 60 * 60 * 24;

const getCategoryBreakdown = async ({ userId, month = getPreviousMonthKey(normalizeMonthKey(new Date())) }) => {
      const monthKey = normalizeMonthKey(month);
      const cacheKey = `categories:${userId}:${monthKey}`;

      const cachedBreakdown = await getCachedJson(cacheKey);

      if (cachedBreakdown) {
            return cachedBreakdown;
      }

      const result = await query(
                                    `SELECT category, total_amount AS amount
                                     FROM category_summary
                                     WHERE user_id = $1
                                           AND month = DATE_TRUNC('month', $2::timestamptz)
                                     ORDER BY amount DESC, category ASC`,
            [userId, getMonthDate(monthKey)]
      );

      const breakdown = result.rows.map((row) => ({
            category: row.category,
            amount: Number(row.amount || 0),
      }));

      await setCachedJson(cacheKey, breakdown, CACHE_TTL_SECONDS);

      return breakdown;
};

module.exports = {
      name: 'getCategoryBreakdown',
      description: 'Where did I spend my money?',
      getCategoryBreakdown,
};