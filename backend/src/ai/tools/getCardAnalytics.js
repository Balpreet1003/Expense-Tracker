const { query } = require('../../config/db');

const getCardAnalytics = async ({ userId, limit = 10 }) => {
      const safeLimit = Number.isInteger(Number(limit)) && Number(limit) > 0 ? Math.min(Number(limit), 20) : 10;

      const result = await query(
            `SELECT s.card_id,
                    c.card_name,
                    s.total_spent
             FROM card_spending_summary s
             LEFT JOIN cards c ON c.id = s.card_id
             WHERE s.user_id = $1
             ORDER BY s.total_spent DESC, s.card_id ASC
             LIMIT $2`,
            [userId, safeLimit]
      );

      return result.rows.map((row) => ({
            cardId: row.card_id,
            cardName: row.card_name || `Card ${row.card_id}`,
            totalSpent: Number(row.total_spent || 0),
      }));
};

module.exports = {
      name: 'getCardAnalytics',
      description: 'Which card is used most?',
      getCardAnalytics,
};